# services/resume_service.py
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List

from utils.db import get_db
from models.resume import ResumeRequest
from models.user import User
from ai.agents.resume_agent import ResumeAgent
from config.settings import TEMP_DIR

logger = logging.getLogger(__name__)

async def process_resume(user_id: int, file_path: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Process a resume file and extract structured information
    
    Args:
        user_id: User ID
        file_path: Path to the resume file
        
    Returns:
        Tuple of (success, resume_data)
    """
    try:
        # Make sure the file exists
        if not os.path.exists(file_path):
            logger.error(f"Resume file not found: {file_path}")
            return False, None
        
        # Use AI agent to parse resume
        resume_data = await ResumeAgent.parse_resume(file_path)
        
        if not resume_data:
            logger.error(f"Failed to parse resume for user {user_id}")
            return False, None
        
        logger.info(f"Successfully parsed resume for user {user_id}")
        
        # Clean up temporary file
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Error removing temporary file {file_path}: {str(e)}")
        
        return True, resume_data
    
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return False, None

async def generate_custom_resume(user_id: int, job_id: str) -> Tuple[bool, Optional[str]]:
    """
    Generate a customized resume for a specific job
    
    Args:
        user_id: User ID
        job_id: Job ID
        
    Returns:
        Tuple of (success, request_id)
    """
    try:
        # Get user's resume data
        from utils.db import get_db
        from sqlalchemy.future import select
        
        async with get_db() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user or not user.has_resume or not user.resume_data:
                logger.error(f"User {user_id} has no resume data")
                return False, None
            
            resume_data = user.resume_data
        
        # Get job data
        from services.job_service import fetch_jobs
        
        jobs = await fetch_jobs(limit=1, job_id=job_id)
        
        if not jobs:
            logger.error(f"Job {job_id} not found")
            return False, None
        
        job_data = jobs[0]
        
        # Create a resume request record
        async with get_db() as db:
            resume_request = ResumeRequest(
                user_id=user_id,
                job_id=job_id,
                status="pending",
                original_resume=json.dumps(resume_data)
            )
            
            db.add(resume_request)
            await db.commit()
            await db.refresh(resume_request)
            
            request_id = resume_request.request_id
        
        # Start async task to generate resume
        from tasks.resume_processing import generate_resume_task
        generate_resume_task.delay(user_id, job_id, request_id)
        
        return True, request_id
    
    except Exception as e:
        logger.error(f"Error generating custom resume: {str(e)}")
        return False, None

async def get_resume_request_status(request_id: str) -> Dict[str, Any]:
    """
    Get the status of a resume request
    
    Args:
        request_id: Resume request ID
        
    Returns:
        Dictionary with request status info
    """
    try:
        from sqlalchemy.future import select
        
        async with get_db() as db:
            result = await db.execute(
                select(ResumeRequest).where(ResumeRequest.request_id == request_id)
            )
            
            request = result.scalar_one_or_none()
            
            if not request:
                return {"status": "not_found", "message": "Resume request not found"}
            
            response = {
                "status": request.status,
                "created_at": request.created_at.isoformat(),
                "updated_at": request.updated_at.isoformat(),
                "job_id": request.job_id
            }
            
            if request.status == "completed":
                response["completed_at"] = request.updated_at.isoformat()
                response["processing_time"] = request.processing_time
            
            return response
    
    except Exception as e:
        logger.error(f"Error getting resume request status: {str(e)}")
        return {"status": "error", "message": "Error getting status"}

async def get_user_resume_requests(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all resume requests for a user
    
    Args:
        user_id: User ID
        
    Returns:
        List of resume request info dictionaries
    """
    try:
        from sqlalchemy.future import select
        
        async with get_db() as db:
            result = await db.execute(
                select(ResumeRequest)
                .where(ResumeRequest.user_id == user_id)
                .order_by(ResumeRequest.created_at.desc())
            )
            
            requests = result.scalars().all()
            
            return [
                {
                    "request_id": req.request_id,
                    "job_id": req.job_id,
                    "status": req.status,
                    "created_at": req.created_at.isoformat(),
                    "updated_at": req.updated_at.isoformat(),
                    "processing_time": req.processing_time
                }
                for req in requests
            ]
    
    except Exception as e:
        logger.error(f"Error getting user resume requests: {str(e)}")
        return []

async def save_customized_resume(request_id: str, customized_resume: str) -> bool:
    """
    Save a customized resume
    
    Args:
        request_id: Resume request ID
        customized_resume: Customized resume text
        
    Returns:
        Success boolean
    """
    try:
        from sqlalchemy.future import select
        
        async with get_db() as db:
            result = await db.execute(
                select(ResumeRequest).where(ResumeRequest.request_id == request_id)
            )
            
            request = result.scalar_one_or_none()
            
            if not request:
                logger.error(f"Resume request not found: {request_id}")
                return False
            
            request.customized_resume = customized_resume
            request.status = "completed"
            request.updated_at = datetime.utcnow()
            
            await db.commit()
            
            # Send resume to user
            from services.notification_service import send_resume_notification
            
            # Get user's telegram ID
            result = await db.execute(select(User).where(User.id == request.user_id))
            user = result.scalar_one_or_none()
            
            if user:
                await send_resume_notification(
                    user.telegram_id,
                    customized_resume,
                    request.job_id
                )
            
            return True
    
    except Exception as e:
        logger.error(f"Error saving customized resume: {str(e)}")
        return False