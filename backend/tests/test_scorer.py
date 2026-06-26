"""
tests/test_scorer.py - Unit tests for the ATS scorer
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ml.scorer import (
    calculate_keyword_score, calculate_skill_score,
    calculate_experience_score, calculate_ats_score
)

def test_keyword_score_similar():
    score = calculate_keyword_score(
        "Python developer with FastAPI and Docker experience",
        "Looking for Python developer skilled in FastAPI and Docker"
    )
    assert score > 30

def test_keyword_score_different():
    score = calculate_keyword_score("I love cooking pasta", "Senior Python Engineer")
    assert score < 20

def test_skill_score_perfect():
    score, matched, missing = calculate_skill_score(
        ["Python", "Docker", "FastAPI"],
        ["Python", "Docker", "FastAPI"],
        ""
    )
    assert score == 100.0
    assert len(missing) == 0

def test_skill_score_partial():
    score, matched, missing = calculate_skill_score(
        ["Python"],
        ["Python", "Docker", "Kubernetes"],
        ""
    )
    assert 30 <= score <= 40
    assert "Docker" in missing

def test_experience_score():
    assert calculate_experience_score(5, 3) == 100.0
    assert calculate_experience_score(0, 3) == 0.0
    assert calculate_experience_score(1, 3) < 50

def test_full_ats_score():
    parsed = {
        "raw_text": "Python developer with 4 years FastAPI Docker AWS experience",
        "skills": ["Python", "FastAPI", "Docker", "AWS"],
        "total_experience_years": 4
    }
    job = {
        "title": "Senior Python Developer",
        "description": "Looking for Python developer with FastAPI Docker AWS",
        "required_skills": ["Python", "FastAPI", "Docker"],
        "experience_years": 3
    }
    result = calculate_ats_score(parsed, job)
    assert result["ats_score"] > 50
    assert result["recommendation"] in ["Selected", "Maybe", "Rejected"]
    assert isinstance(result["skill_match"], list)
    assert isinstance(result["missing_skills"], list)
