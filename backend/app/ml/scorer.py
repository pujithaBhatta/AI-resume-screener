"""
ml/scorer.py - ATS Scoring Engine
====================================
Calculates how well a resume matches a job description using:

1. KEYWORD SCORE (30%): Do the resume's keywords match job keywords?
   - Uses TF-IDF vectorization + cosine similarity

2. SKILL SCORE (40%): Do the candidate's skills match required skills?
   - Direct skill matching (exact + partial)

3. SEMANTIC SCORE (20%): Does the resume meaning match the job semantically?
   - Uses Sentence Transformers (BERT) for deep meaning comparison
   - Catches synonyms: "built" vs "developed", "ML" vs "machine learning"

4. EXPERIENCE SCORE (10%): Does experience meet the minimum requirement?

FINAL SCORE = weighted combination of all 4 scores (0-100)
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK data
for resource in ['stopwords', 'punkt', 'averaged_perceptron_tagger']:
    try:
        nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' 
                       else f'corpora/{resource}' if resource == 'stopwords'
                       else f'taggers/{resource}')
    except LookupError:
        nltk.download(resource, quiet=True)

# Try to load sentence transformers (optional - slower but more accurate)
try:
    from sentence_transformers import SentenceTransformer
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    SEMANTIC_AVAILABLE = True
    print("✅ Sentence Transformer loaded for semantic scoring")
except Exception:
    SEMANTIC_AVAILABLE = False
    print("⚠️ Sentence Transformers not available. Using TF-IDF only.")

STOP_WORDS = set(stopwords.words('english'))


# ============================================================
# Text Preprocessing
# ============================================================

def preprocess_text(text: str) -> str:
    """
    Cleans and normalizes text for NLP processing.
    
    Steps:
    1. Lowercase everything
    2. Remove special characters (keep letters, numbers, spaces)
    3. Remove stopwords (the, is, at, which, etc.)
    4. Return clean text
    """
    if not text:
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove special characters except spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Tokenize and remove stopwords
    try:
        tokens = word_tokenize(text)
        tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1]
        return ' '.join(tokens)
    except Exception:
        return text


# ============================================================
# Individual Scoring Functions
# ============================================================

def calculate_keyword_score(resume_text: str, job_text: str) -> float:
    """
    Calculates keyword overlap score using TF-IDF cosine similarity.
    
    TF-IDF (Term Frequency-Inverse Document Frequency):
    - TF: How often a word appears in a document
    - IDF: How unique/important the word is across all documents
    - Together: Gives high scores to important, frequent words
    
    Cosine Similarity:
    - Measures the angle between two TF-IDF vectors
    - 1.0 = identical documents, 0.0 = completely different
    
    Returns: Score from 0 to 100
    """
    resume_clean = preprocess_text(resume_text)
    job_clean = preprocess_text(job_text)
    
    if not resume_clean or not job_clean:
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),   # Consider single words AND word pairs
            max_features=5000,     # Limit vocabulary size for performance
            min_df=1
        )
        
        # Fit and transform both texts
        tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])
        
        # Calculate cosine similarity between the two vectors
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return round(float(similarity) * 100, 2)
    
    except Exception:
        return 0.0


def calculate_skill_score(
    resume_skills: List[str],
    required_skills: List[str],
    job_text: str
) -> Tuple[float, List[str], List[str]]:
    """
    Calculates skill match score and identifies matched/missing skills.
    
    Returns:
        (score, matched_skills, missing_skills)
    """
    if not required_skills:
        # If no explicit skills listed, extract from job text
        from app.ml.parser import extract_skills
        required_skills = extract_skills(job_text)
    
    if not required_skills:
        return 50.0, [], []  # Default score when no skills to compare
    
    # Normalize to lowercase for comparison
    resume_skills_lower = {s.lower() for s in resume_skills}
    required_skills_lower = {s.lower() for s in required_skills}
    
    matched = []
    missing = []
    
    for skill in required_skills:
        skill_lower = skill.lower()
        
        # Check exact match or partial match
        if skill_lower in resume_skills_lower:
            matched.append(skill)
        else:
            # Check partial match (e.g., "React.js" matches "React")
            partial_match = any(
                skill_lower in rs or rs in skill_lower
                for rs in resume_skills_lower
                if len(rs) > 2
            )
            if partial_match:
                matched.append(skill)
            else:
                missing.append(skill)
    
    score = (len(matched) / len(required_skills)) * 100 if required_skills else 0
    
    return round(score, 2), matched, missing


def calculate_semantic_score(resume_text: str, job_text: str) -> float:
    """
    Calculates semantic similarity using BERT sentence embeddings.
    
    Unlike TF-IDF (word matching), BERT understands MEANING.
    Example: "built REST APIs" and "developed web services" score high
    even though they share no keywords.
    
    Returns: Score from 0 to 100
    """
    if not SEMANTIC_AVAILABLE:
        return 0.0
    
    if not resume_text or not job_text:
        return 0.0
    
    try:
        # Truncate to first 512 tokens (BERT limit)
        resume_short = resume_text[:2000]
        job_short = job_text[:1000]
        
        # Generate embeddings (numerical representation of meaning)
        embeddings = semantic_model.encode([resume_short, job_short])
        
        # Cosine similarity between embeddings
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        return round(float(similarity) * 100, 2)
    
    except Exception:
        return 0.0


def calculate_experience_score(
    candidate_years: float,
    required_years: int
) -> float:
    """
    Scores experience match.
    
    - Meets or exceeds requirement: 100
    - Close to requirement: proportional score
    - No experience required: 100
    """
    if required_years <= 0:
        return 100.0
    
    if candidate_years >= required_years:
        # Bonus for significantly more experience (capped at 100)
        bonus = min(10, (candidate_years - required_years) * 2)
        return min(100.0, 100.0 + bonus)
    
    # Partial credit for some experience
    ratio = candidate_years / required_years
    return round(ratio * 100, 2)


# ============================================================
# Main Scoring Function
# ============================================================

def calculate_ats_score(
    parsed_resume: Dict[str, Any],
    job: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculates the complete ATS score for a resume against a job.
    
    Parameters:
        parsed_resume: Output from parser.py (name, skills, experience, etc.)
        job: Job document from MongoDB (title, description, required_skills, etc.)
    
    Returns:
        Dictionary with final score, component scores, matched/missing skills,
        recommendation, and improvement suggestions.
    """
    
    resume_text = parsed_resume.get("raw_text", "")
    resume_skills = parsed_resume.get("skills", [])
    experience_years = parsed_resume.get("total_experience_years", 0)
    
    job_text = f"{job.get('title', '')} {job.get('description', '')}"
    required_skills = job.get("required_skills", [])
    required_experience = job.get("experience_years", 0)
    
    # ---- Component Scores ----
    
    # 1. Keyword score (TF-IDF)
    keyword_score = calculate_keyword_score(resume_text, job_text)
    
    # 2. Skill score
    skill_score, matched_skills, missing_skills = calculate_skill_score(
        resume_skills, required_skills, job_text
    )
    
    # 3. Semantic score (BERT)
    semantic_score = calculate_semantic_score(resume_text, job_text)
    
    # 4. Experience score
    experience_score = calculate_experience_score(experience_years, required_experience)
    
    # ---- Weighted Final Score ----
    # Weights: Skills (40%) > Keywords (30%) > Semantic (20%) > Experience (10%)
    if SEMANTIC_AVAILABLE:
        final_score = (
            skill_score * 0.40 +
            keyword_score * 0.30 +
            semantic_score * 0.20 +
            experience_score * 0.10
        )
    else:
        # Without semantic model, redistribute weights
        final_score = (
            skill_score * 0.50 +
            keyword_score * 0.40 +
            experience_score * 0.10
        )
    
    final_score = round(min(100.0, final_score), 2)
    
    # ---- Recommendation ----
    if final_score >= 75:
        recommendation = "Selected"
    elif final_score >= 50:
        recommendation = "Maybe"
    else:
        recommendation = "Rejected"
    
    # ---- Improvement Suggestions ----
    suggestions = generate_suggestions(
        missing_skills, experience_years, required_experience,
        keyword_score, final_score
    )
    
    return {
        "ats_score": final_score,
        "component_scores": {
            "keyword_score": keyword_score,
            "skill_score": skill_score,
            "semantic_score": semantic_score,
            "experience_score": experience_score
        },
        "skill_match": matched_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
        "suggestions": suggestions
    }


def generate_suggestions(
    missing_skills: List[str],
    candidate_years: float,
    required_years: int,
    keyword_score: float,
    final_score: float
) -> List[str]:
    """Generates actionable recommendations to improve the resume/candidacy."""
    suggestions = []
    
    if missing_skills:
        top_missing = missing_skills[:5]
        suggestions.append(
            f"Add these missing skills to your resume: {', '.join(top_missing)}"
        )
    
    if candidate_years < required_years:
        gap = required_years - candidate_years
        suggestions.append(
            f"The role requires {required_years} years experience. "
            f"You have ~{candidate_years:.0f} years. "
            f"Highlight relevant projects to compensate for the {gap:.0f}-year gap."
        )
    
    if keyword_score < 40:
        suggestions.append(
            "Your resume lacks keywords from the job description. "
            "Mirror the language used in the job posting."
        )
    
    if final_score < 50:
        suggestions.append(
            "Tailor your resume specifically for this role. "
            "Add quantifiable achievements and use action verbs."
        )
    
    if final_score >= 75:
        suggestions.append(
            "Strong match! Prepare for technical interviews "
            "focusing on your listed skills."
        )
    
    return suggestions


def generate_summary(parsed_resume: Dict, job: Dict, score_result: Dict) -> str:
    """
    Generates a human-readable AI summary of the candidate.
    """
    name = parsed_resume.get("name", "The candidate")
    skills = parsed_resume.get("skills", [])[:6]
    exp_years = parsed_resume.get("total_experience_years", 0)
    score = score_result.get("ats_score", 0)
    recommendation = score_result.get("recommendation", "")
    matched = score_result.get("skill_match", [])[:4]
    missing = score_result.get("missing_skills", [])[:3]
    
    skills_str = ", ".join(skills) if skills else "various technologies"
    matched_str = ", ".join(matched) if matched else "some required skills"
    
    summary = (
        f"{name} is a professional with approximately {exp_years:.0f} years of experience, "
        f"skilled in {skills_str}. "
        f"This candidate achieved an ATS score of {score}/100 for the {job.get('title', 'position')}. "
    )
    
    if matched:
        summary += f"Key matching skills include: {matched_str}. "
    
    if missing:
        summary += f"Notable skill gaps: {', '.join(missing)}. "
    
    summary += f"Overall recommendation: {recommendation}."
    
    return summary
