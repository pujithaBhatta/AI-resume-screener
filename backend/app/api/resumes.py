"""
api/resumes.py - Resume Upload & Management Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import os, shutil

from app.services.auth_service import get_current_user
from app.database import get_collection
from app.config import settings
from app.ml.parser import parse_resume

router = APIRouter()


@router.post("/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    job_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload one or multiple resume files (PDF or DOCX).
    Automatically parses each resume after upload.
    """
    resumes_col = get_collection("resumes")
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    results = []
    
    for file in files:
        # Validate file type
        allowed = [".pdf", ".docx", ".txt"]
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"Unsupported file type. Allowed: {', '.join(allowed)}"
            })
            continue
        
        # Validate file size
        content = await file.read()
        if len(content) > settings.max_file_size_mb * 1024 * 1024:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"File too large. Max: {settings.max_file_size_mb}MB"
            })
            continue
        
        # Save file to disk
        safe_name = f"{datetime.utcnow().timestamp()}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(settings.upload_dir, safe_name)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Parse the resume
        try:
            parsed_data = parse_resume(file_path, file.filename)
        except Exception as e:
            parsed_data = {"raw_text": "", "name": None, "email": None,
                          "phone": None, "skills": [], "education": [],
                          "experience": [], "total_experience_years": 0}
        
        # Save to MongoDB
        resume_doc = {
            "filename": file.filename,
            "file_path": file_path,
            "parsed_data": parsed_data,
            "job_id": job_id,
            "ats_score": None,
            "skill_match": [],
            "missing_skills": [],
            "recommendation": None,
            "summary": None,
            "uploaded_at": datetime.utcnow(),
            "uploaded_by": current_user["id"]
        }
        
        result = await resumes_col.insert_one(resume_doc)
        
        results.append({
            "id": str(result.inserted_id),
            "filename": file.filename,
            "status": "success",
            "candidate_name": parsed_data.get("name"),
            "skills_found": len(parsed_data.get("skills", [])),
            "message": "Resume uploaded and parsed successfully"
        })
    
    return {"uploaded": len(results), "results": results}


@router.get("/")
async def list_resumes(
    job_id: Optional[str] = None,
    search: Optional[str] = None,
    min_score: Optional[float] = None,
    recommendation: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all resumes with optional filtering."""
    resumes_col = get_collection("resumes")
    
    query = {}
    if job_id:
        query["job_id"] = job_id
    if min_score is not None:
        query["ats_score"] = {"$gte": min_score}
    if recommendation:
        query["recommendation"] = recommendation
    if search:
        query["$or"] = [
            {"parsed_data.name": {"$regex": search, "$options": "i"}},
            {"parsed_data.email": {"$regex": search, "$options": "i"}},
            {"filename": {"$regex": search, "$options": "i"}},
        ]
    
    resumes = []
    async for r in resumes_col.find(query).sort("ats_score", -1):
        resumes.append({
            "id": str(r["_id"]),
            "filename": r["filename"],
            "candidate_name": r.get("parsed_data", {}).get("name"),
            "candidate_email": r.get("parsed_data", {}).get("email"),
            "skills": r.get("parsed_data", {}).get("skills", []),
            "job_id": r.get("job_id"),
            "ats_score": r.get("ats_score"),
            "skill_match": r.get("skill_match", []),
            "missing_skills": r.get("missing_skills", []),
            "recommendation": r.get("recommendation"),
            "summary": r.get("summary"),
            "uploaded_at": r["uploaded_at"].isoformat()
        })
    
    return resumes


@router.get("/{resume_id}")
async def get_resume(resume_id: str, current_user: dict = Depends(get_current_user)):
    """Get full details of a specific resume."""
    resumes_col = get_collection("resumes")
    
    try:
        r = await resumes_col.find_one({"_id": ObjectId(resume_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "id": str(r["_id"]),
        "filename": r["filename"],
        "parsed_data": r.get("parsed_data", {}),
        "job_id": r.get("job_id"),
        "ats_score": r.get("ats_score"),
        "skill_match": r.get("skill_match", []),
        "missing_skills": r.get("missing_skills", []),
        "recommendation": r.get("recommendation"),
        "summary": r.get("summary"),
        "uploaded_at": r["uploaded_at"].isoformat()
    }


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a resume."""
    resumes_col = get_collection("resumes")
    
    try:
        r = await resumes_col.find_one({"_id": ObjectId(resume_id)})
        if r and r.get("file_path") and os.path.exists(r["file_path"]):
            os.remove(r["file_path"])
        result = await resumes_col.delete_one({"_id": ObjectId(resume_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {"message": "Resume deleted successfully"}
