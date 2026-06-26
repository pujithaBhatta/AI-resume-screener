"""
api/jobs.py - Job Description Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.resume import JobCreateRequest, JobResponse
from app.services.auth_service import get_current_user
from app.database import get_collection

router = APIRouter()


def job_to_response(job: dict) -> dict:
    job["id"] = str(job["_id"])
    return job


@router.post("/", response_model=dict)
async def create_job(request: JobCreateRequest, current_user: dict = Depends(get_current_user)):
    """Create a new job description."""
    jobs_col = get_collection("jobs")
    
    job_doc = {
        "title": request.title,
        "description": request.description,
        "required_skills": request.required_skills,
        "experience_years": request.experience_years,
        "created_by": current_user["id"],
        "created_at": datetime.utcnow(),
        "resume_count": 0
    }
    
    result = await jobs_col.insert_one(job_doc)
    
    return {
        "id": str(result.inserted_id),
        "message": "Job created successfully",
        "title": request.title
    }


@router.get("/", response_model=List[dict])
async def list_jobs(current_user: dict = Depends(get_current_user)):
    """List all job descriptions."""
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")
    
    jobs = []
    async for job in jobs_col.find().sort("created_at", -1):
        job_id = str(job["_id"])
        count = await resumes_col.count_documents({"job_id": job_id})
        jobs.append({
            "id": job_id,
            "title": job["title"],
            "description": job["description"],
            "required_skills": job.get("required_skills", []),
            "experience_years": job.get("experience_years", 0),
            "resume_count": count,
            "created_at": job["created_at"].isoformat()
        })
    
    return jobs


@router.get("/{job_id}", response_model=dict)
async def get_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific job description."""
    jobs_col = get_collection("jobs")
    
    try:
        job = await jobs_col.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": str(job["_id"]),
        "title": job["title"],
        "description": job["description"],
        "required_skills": job.get("required_skills", []),
        "experience_years": job.get("experience_years", 0),
        "created_at": job["created_at"].isoformat()
    }


@router.delete("/{job_id}")
async def delete_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a job description."""
    jobs_col = get_collection("jobs")
    
    try:
        result = await jobs_col.delete_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}
