
# api/routes/jobs.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from utils.auth import get_admin_user
from services.job_service import fetch_jobs

# Create router
router = APIRouter()

@router.get("/")
async def get_jobs(
    limit: int = 10,
    location: Optional[str] = None,
    title: Optional[str] = None,
    company: Optional[str] = None,
    experience: Optional[str] = None,
    job_type: Optional[str] = None
):
    """
    Get jobs from API
    """
    jobs = await fetch_jobs(
        limit=limit,
        location=location,
        title=title,
        company=company,
        experience=experience,
        job_type=job_type
    )
    
    return jobs

@router.get("/saved/{user_id}")
async def get_saved_jobs(
    user_id: int,
    admin=Depends(get_admin_user)
):
    """
    Get jobs saved by a user (admin only)
    """
    from utils.db import get_db
    from sqlalchemy.future import select
    from models.job import SavedJob
    
    async with get_db() as db:
        result = await db.execute(
            select(SavedJob)
            .where(SavedJob.user_id == user_id)
            .order_by(SavedJob.saved_at.desc())
        )
        
        saved_jobs = result.scalars().all()
        
        return [
            {
                "id": job.id,
                "job_id": job.job_id,
                "saved_at": job.saved_at.isoformat(),
                "notes": job.notes,
                "job_data": job.job_data
            }
            for job in saved_jobs
        ]
