"""
tests/test_parser.py - Unit tests for the resume parser
Run with: pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ml.parser import (
    extract_email, extract_phone, extract_skills
)

def test_extract_email():
    assert extract_email("Contact: john@example.com for details") == "john@example.com"
    assert extract_email("No email here") is None

def test_extract_phone():
    assert extract_phone("Call +91-9876543210") is not None
    assert extract_phone("No phone") is None

def test_extract_skills():
    text = "I know Python, React, and Docker very well"
    skills = extract_skills(text)
    skill_lower = [s.lower() for s in skills]
    assert "python" in skill_lower
    assert "react" in skill_lower
    assert "docker" in skill_lower

def test_extract_skills_case_insensitive():
    text = "PYTHON DEVELOPER with FASTAPI experience"
    skills = extract_skills(text)
    skill_lower = [s.lower() for s in skills]
    assert "python" in skill_lower
