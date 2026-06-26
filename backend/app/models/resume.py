"""
models/resume.py - Resume & Job Data Models
=============================================
These models define the structure of resume and job data throughout the app.

KEY CONCEPT - Optional vs Required fields:
- Required: title: str         ← must be provided, no default
- Optional: phone: Optional[str] = None  ← can be None/missing
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================
# Enums (predefined choices)
# ============================================================

class RecommendationType(str, Enum):
    """
    Interview recommendation values.
    Using an Enum ensures only valid values are accepted.
    """
    SELECTED = "Selected"
    REJECTED = "Rejected"
    MAYBE = "Maybe"


# ============================================================
# Sub-models (nested objects within a resume)
# ============================================================

class EducationEntry(BaseModel):
    """One education entry (someone may have multiple degrees)."""
    degree: Optional[str] = None           # "B.Tech Computer Science"
    institution: Optional[str] = None      # "IIT Bombay"
    year: Optional[str] = None             # "2020"
    gpa: Optional[str] = None              # "3.8/4.0"


class ExperienceEntry(BaseModel):
    """One work experience entry."""
    title: Optional[str] = None            # "Software Engineer"
    company: Optional[str] = None          # "Google"
    duration: Optional[str] = None         # "2 years"
    description: Optional[str] = None      # "Built microservices..."


class ParsedResumeData(BaseModel):
    """
    Structured data extracted from a raw resume by our NLP parser.
    All fields are Optional because not every resume has all sections.
    """
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    education: List[EducationEntry] = []
    experience: List[ExperienceEntry] = []
    total_experience_years: float = 0.0
    raw_text: str = ""


# ============================================================
# Resume Models
# ============================================================

class ResumeUploadResponse(BaseModel):
    """Returned immediately after a resume is uploaded."""
    id: str
    filename: str
    status: str = "uploaded"
    message: str


class ResumeResponse(BaseModel):
    """Full resume data returned from the API."""
    id: str
    filename: str
    parsed_data: Optional[ParsedResumeData] = None
    job_id: Optional[str] = None
    ats_score: Optional[float] = None
    skill_match: List[str] = []
    missing_skills: List[str] = []
    recommendation: Optional[str] = None
    summary: Optional[str] = None
    uploaded_at: datetime
    
    class Config:
        populate_by_name = True


# ============================================================
# Job Description Models
# ============================================================

class JobCreateRequest(BaseModel):
    """Data to create a new job description."""
    title: str = Field(..., min_length=3, max_length=200,
                       description="Job title, e.g. 'Senior Python Developer'")
    description: str = Field(..., min_length=50,
                              description="Full job description text")
    required_skills: List[str] = Field(default=[],
                                        description="List of required skills")
    experience_years: int = Field(default=0, ge=0, le=30,
                                   description="Minimum years of experience required")


class JobResponse(BaseModel):
    """Job data returned from the API."""
    id: str
    title: str
    description: str
    required_skills: List[str]
    experience_years: int
    resume_count: int = 0          # How many resumes have been screened for this job
    created_at: datetime
    
    class Config:
        populate_by_name = True


# ============================================================
# Screening / Scoring Models
# ============================================================

class ScreeningRequest(BaseModel):
    """
    Request to run ATS scoring on selected resumes against a job.
    
    Example:
        { "job_id": "abc123", "resume_ids": ["r1", "r2", "r3"] }
    """
    job_id: str
    resume_ids: List[str] = Field(..., min_length=1,
                                   description="List of resume IDs to screen")


class CandidateRanking(BaseModel):
    """One candidate's ranking result, used in the ranked list response."""
    resume_id: str
    candidate_name: Optional[str] = None
    filename: str
    ats_score: float
    skill_match: List[str]
    missing_skills: List[str]
    recommendation: str
    rank: int
