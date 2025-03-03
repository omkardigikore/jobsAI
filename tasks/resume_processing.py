# tasks/resume_processing.py
import logging
import asyncio
import json
from datetime import datetime

from config.celery import app
from ai.agents.resume_agent import ResumeAgent

logger = logging.getLogger(__name__)

@app.task
def generate_resume_task(user_id: int, job_id: str, request_id: str):
    """
    Celery task to generate a customized resume
    This is a wrapper that calls the async function
    """
    asyncio.run(_generate_resume_async(user_id, job_id, request_id))

async def _generate_resume_async(user_id: int, job_id: str, request_id: str):
    """
    Async implementation of the resume generation task
    """
    logger.info(f"Starting resume generation for user {user_id}, job {job_id}")
    
    try:
        # Get resume data and job data
        from utils.db import get_db
        from sqlalchemy.future import select
        from models.user import User
        from models.resume import ResumeRequest
        
        # Update request status to processing
        async with get_db() as db:
            result = await db.execute(
                select(ResumeRequest).where(ResumeRequest.request_id == request_id)
            )
            
            resume_request = result.scalar_one_or_none()
            
            if not resume_request:
                logger.error(f"Resume request not found: {request_id}")
                return
            
            resume_request.status = "processing"
            resume_request.updated_at = datetime.utcnow()
            
            await db.commit()
        
        # Get user's resume data
        async with get_db() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user or not user.has_resume or not user.resume_data:
                logger.error(f"User {user_id} has no resume data")
                
                # Update request status to failed
                resume_request.status = "failed"
                resume_request.updated_at = datetime.utcnow()
                
                await db.commit()
                return
            
            resume_data = user.resume_data
        
        # Get job data
        from services.job_service import fetch_jobs
        
        jobs = await fetch_jobs(limit=1, job_id=job_id)
        
        if not jobs:
            logger.error(f"Job {job_id} not found")
            
            # Update request status to failed
            async with get_db() as db:
                result = await db.execute(
                    select(ResumeRequest).where(ResumeRequest.request_id == request_id)
                )
                
                resume_request = result.scalar_one_or_none()
                
                if resume_request:
                    resume_request.status = "failed"
                    resume_request.updated_at = datetime.utcnow()
                    
                    await db.commit()
            
            return
        
        job_data = jobs[0]
        
        # Generate customized resume
        start_time = datetime.utcnow()
        
        customized_resume = await ResumeAgent.customize_resume(
            user_id=user_id,
            job_data=job_data,
            resume_data=resume_data
        )
        
        end_time = datetime.utcnow()
        processing_time = int((end_time - start_time).total_seconds())
        
        if not customized_resume:
            logger.error(f"Failed to generate customized resume")
            
            # Update request status to failed
            async with get_db() as db:
                result = await db.execute(
                    select(ResumeRequest).where(ResumeRequest.request_id == request_id)
                )
                
                resume_request = result.scalar_one_or_none()
                
                if resume_request:
                    resume_request.status = "failed"
                    resume_request.updated_at = datetime.utcnow()
                    
                    await db.commit()
            
            return
        
        # Save customized resume
        from services.resume_service import save_customized_resume
        
        success = await save_customized_resume(request_id, customized_resume)
        
        if success:
            logger.info(f"Successfully generated customized resume for user {user_id}, job {job_id}")
            
            # Update request with processing time
            async with get_db() as db:
                result = await db.execute(
                    select(ResumeRequest).where(ResumeRequest.request_id == request_id)
                )
                
                resume_request = result.scalar_one_or_none()
                
                if resume_request:
                    resume_request.processing_time = processing_time
                    
                    await db.commit()
        else:
            logger.error(f"Failed to save customized resume")
    
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        
        # Update request status to failed
        try:
            from utils.db import get_db
            from sqlalchemy.future import select
            from models.resume import ResumeRequest
            
            async with get_db() as db:
                result = await db.execute(
                    select(ResumeRequest).where(ResumeRequest.request_id == request_id)
                )
                
                resume_request = result.scalar_one_or_none()
                
                if resume_request:
                    resume_request.status = "failed"
                    resume_request.updated_at = datetime.utcnow()
                    
                    await db.commit()
        except Exception as db_error:
            logger.error(f"Error updating resume request status: {str(db_error)}")