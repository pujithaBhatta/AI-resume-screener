"""
api/analytics.py - Dashboard Analytics Endpoints
"""

from fastapi import APIRouter, Depends
from app.services.auth_service import get_current_user
from app.database import get_collection

router = APIRouter()


@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Returns overall statistics for the dashboard."""
    resumes_col = get_collection("resumes")
    jobs_col = get_collection("jobs")

    total_resumes = await resumes_col.count_documents({})
    total_jobs = await jobs_col.count_documents({})
    selected = await resumes_col.count_documents({"recommendation": "Selected"})
    rejected = await resumes_col.count_documents({"recommendation": "Rejected"})
    maybe = await resumes_col.count_documents({"recommendation": "Maybe"})
    screened = await resumes_col.count_documents({"ats_score": {"$ne": None}})

    # Average ATS score
    pipeline = [{"$match": {"ats_score": {"$ne": None}}},
                {"$group": {"_id": None, "avg": {"$avg": "$ats_score"}}}]
    avg_result = await resumes_col.aggregate(pipeline).to_list(1)
    avg_score = round(avg_result[0]["avg"], 1) if avg_result else 0

    # Score distribution buckets
    score_dist = []
    buckets = [(0, 25, "0-25"), (25, 50, "25-50"), (50, 75, "50-75"), (75, 100, "75-100")]
    for low, high, label in buckets:
        count = await resumes_col.count_documents({
            "ats_score": {"$gte": low, "$lt": high if high < 100 else 101}
        })
        score_dist.append({"range": label, "count": count})

    return {
        "total_resumes": total_resumes,
        "total_jobs": total_jobs,
        "screened": screened,
        "selected": selected,
        "rejected": rejected,
        "maybe": maybe,
        "avg_score": avg_score,
        "score_distribution": score_dist
    }


@router.get("/top-skills")
async def get_top_skills(current_user: dict = Depends(get_current_user)):
    """Returns the most common skills across all resumes."""
    resumes_col = get_collection("resumes")
    pipeline = [
        {"$unwind": "$parsed_data.skills"},
        {"$group": {"_id": "$parsed_data.skills", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    results = await resumes_col.aggregate(pipeline).to_list(15)
    return [{"skill": r["_id"], "count": r["count"]} for r in results]
