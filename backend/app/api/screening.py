"""
api/screening.py - ATS Scoring Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime

from app.services.auth_service import get_current_user
from app.database import get_collection
from app.ml.scorer import calculate_ats_score, generate_summary
from app.models.resume import ScreeningRequest

router = APIRouter()


@router.post("/score")
async def score_resumes(request: ScreeningRequest, current_user: dict = Depends(get_current_user)):
    """
    Run ATS scoring on selected resumes against a job description.
    """
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")

    # Get job
    try:
        job = await jobs_col.find_one({"_id": ObjectId(request.job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results = []

    for resume_id in request.resume_ids:
        try:
            resume = await resumes_col.find_one({"_id": ObjectId(resume_id)})
        except Exception:
            continue

        if not resume:
            continue

        parsed = resume.get("parsed_data", {})

        # Calculate ATS score
        score_result = calculate_ats_score(parsed, job)

        # Generate AI summary
        summary = generate_summary(parsed, job, score_result)

        # Update resume in database
        await resumes_col.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {
                "job_id": request.job_id,
                "ats_score": score_result["ats_score"],
                "skill_match": score_result["skill_match"],
                "missing_skills": score_result["missing_skills"],
                "recommendation": score_result["recommendation"],
                "summary": summary,
                "component_scores": score_result["component_scores"],
                "suggestions": score_result["suggestions"],
                "scored_at": datetime.utcnow()
            }}
        )

        results.append({
            "resume_id": resume_id,
            "candidate_name": parsed.get("name"),
            "ats_score": score_result["ats_score"],
            "recommendation": score_result["recommendation"],
            "skill_match": score_result["skill_match"],
            "missing_skills": score_result["missing_skills"]
        })

    # Sort by score descending and add ranks
    results.sort(key=lambda x: x["ats_score"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return {
        "job_title": job["title"],
        "total_screened": len(results),
        "results": results
    }


@router.get("/rankings/{job_id}")
async def get_rankings(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get ranked candidates for a specific job."""
    resumes_col = get_collection("resumes")

    candidates = []
    async for r in resumes_col.find({"job_id": job_id, "ats_score": {"$ne": None}}).sort("ats_score", -1):
        candidates.append({
            "resume_id": str(r["_id"]),
            "candidate_name": r.get("parsed_data", {}).get("name", "Unknown"),
            "filename": r["filename"],
            "ats_score": r.get("ats_score", 0),
            "skill_match": r.get("skill_match", []),
            "missing_skills": r.get("missing_skills", []),
            "recommendation": r.get("recommendation", "Pending"),
            "summary": r.get("summary", ""),
            "suggestions": r.get("suggestions", [])
        })

    for i, c in enumerate(candidates):
        c["rank"] = i + 1

    return candidates
