# services/job_service.py
import logging
import json
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from config.settings import JOBS_API_KEY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from utils.db import get_db
from ai.agents.job_matching_agent import JobMatchingAgent

logger = logging.getLogger(__name__)

# Jobs API Configuration
JOBS_API_BASE_URL = "https://jobs.indianapi.in"
JOBS_API_HEADERS = {
    "X-Api-Key": JOBS_API_KEY
}

async def fetch_jobs(
    limit: int = 20,
    location: Optional[str] = None,
    title: Optional[str] = None,
    company: Optional[str] = None,
    experience: Optional[str] = None,
    job_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch jobs from the Jobs API with optional filters
    
    Args:
        limit: Maximum number of jobs to return
        location: Filter by job location
        title: Filter by job title
        company: Filter by company name
        experience: Filter by experience level
        job_type: Filter by job type (Full Time, Part Time, etc.)
        
    Returns:
        List of job dictionaries
    """
    try:
        # Build query parameters
        params = {"limit": str(limit)}
        
        if location:
            params["location"] = location
        if title:
            params["title"] = title
        if company:
            params["company"] = company
        if experience:
            params["experience"] = experience
        if job_type:
            params["job_type"] = job_type
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{JOBS_API_BASE_URL}/jobs",
                headers=JOBS_API_HEADERS,
                params=params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Jobs API error: {response.status} - {error_text}")
                    return []
                
                jobs_data = await response.json()
                return jobs_data
    
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        return []

async def get_personalized_jobs_for_user(user_id: int, limit: int = 5) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Get personalized job recommendations for a user based on their resume
    
    Args:
        user_id: User ID
        limit: Maximum number of jobs to return
        
    Returns:
        Tuple of (list of jobs, success boolean)
    """
    try:
        # Get user and resume data
        async with get_db() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user or not user.has_resume or not user.resume_data:
                logger.warning(f"User {user_id} has no resume data for job matching")
                return [], False
        
        # Get user's location from resume data
        resume_data = user.resume_data
        user_location = None
        
        if "contact_info" in resume_data and "location" in resume_data["contact_info"]:
            user_location = resume_data["contact_info"]["location"]
        
        # Extract experience level from resume
        experience_level = calculate_experience_level(resume_data)
        
        # Fetch jobs with basic filtering
        jobs = await fetch_jobs(
            limit=limit * 3,  # Fetch more jobs for better matching
            location=user_location,
            experience=experience_level
        )
        
        if not jobs:
            logger.warning("No jobs returned from API")
            return [], False
        
        # Use AI to match jobs to the user's resume
        matched_jobs = await JobMatchingAgent.match_jobs_to_resume(jobs, resume_data)
        
        # Return top matches, limited to requested number
        return matched_jobs[:limit], True
    
    except Exception as e:
        logger.error(f"Error getting personalized jobs: {str(e)}")
        return [], False

def calculate_experience_level(resume_data: Dict[str, Any]) -> Optional[str]:
    """
    Calculate experience level based on work history in resume
    
    Args:
        resume_data: Parsed resume data
        
    Returns:
        Experience level string or None
    """
    try:
        if "work_experience" not in resume_data or not resume_data["work_experience"]:
            return "Fresher"
        
        # Calculate total experience in years
        total_years = 0
        
        for job in resume_data["work_experience"]:
            if "start_date" in job and job["start_date"]:
                start_date = None
                end_date = datetime.now()
                
                # Parse start date
                try:
                    start_date = datetime.strptime(job["start_date"], "%Y-%m")
                except ValueError:
                    try:
                        start_date = datetime.strptime(job["start_date"], "%Y")
                    except ValueError:
                        continue
                
                # Parse end date if provided
                if "end_date" in job and job["end_date"] and job["end_date"].lower() != "present":
                    try:
                        end_date = datetime.strptime(job["end_date"], "%Y-%m")
                    except ValueError:
                        try:
                            end_date = datetime.strptime(job["end_date"], "%Y")
                        except ValueError:
                            pass
                
                if start_date:
                    # Calculate duration
                    duration = end_date - start_date
                    years = duration.days / 365.25
                    total_years += years
        
        # Determine experience level
        if total_years < 1:
            return "Fresher"
        elif total_years < 3:
            return "1-3 years"
        elif total_years < 5:
            return "3-5 years"
        elif total_years < 8:
            return "5-8 years"
        elif total_years < 12:
            return "8-12 years"
        else:
            return "12+ years"
    
    except Exception as e:
        logger.error(f"Error calculating experience level: {str(e)}")
        return None

async def format_job_for_telegram(job: Dict[str, Any]) -> str:
    """
    Format a job listing for Telegram message
    
    Args:
        job: Job data dictionary
        
    Returns:
        Formatted job text
    """
    try:
        # Format posted date
        posted_date = "Unknown"
        if "posted_date" in job and job["posted_date"]:
            try:
                date_obj = datetime.fromisoformat(job["posted_date"].replace("Z", "+00:00"))
                posted_date = date_obj.strftime("%d %b %Y")
            except:
                posted_date = job["posted_date"]
        
        # Create formatted job text
        job_text = (
            f"🔍 *{job.get('title', 'Job Opening')}*\n\n"
            f"🏢 *Company:* {job.get('company', 'Not specified')}\n"
            f"📍 *Location:* {job.get('location', 'Not specified')}\n"
            f"⏱ *Job Type:* {job.get('job_type', 'Not specified')}\n"
            f"🧠 *Experience:* {job.get('experience', 'Not specified')}\n"
            f"📅 *Posted:* {posted_date}\n\n"
        )
        
        # Add job description (truncated if too long)
        description = job.get('job_description', '')
        if description:
            if len(description) > 300:
                description = description[:297] + "..."
            job_text += f"📋 *Description:*\n{description}\n\n"
        
        # Add skills if available
        if "education_and_skills" in job and job["education_and_skills"]:
            skills = job["education_and_skills"]
            if len(skills) > 200:
                skills = skills[:197] + "..."
            job_text += f"🔧 *Skills:*\n{skills}\n\n"
        
        # Add apply link
        if "apply_link" in job and job["apply_link"]:
            job_text += f"[Apply for this job]({job['apply_link']})\n\n"
        
        # Add customized resume option
        job_text += f"Want a customized resume for this job? Click the button below."
        
        return job_text
    
    except Exception as e:
        logger.error(f"Error formatting job: {str(e)}")
        return "Error formatting job details."

async def save_job_for_user(user_id: int, job_id: str) -> bool:
    """
    Save a job for a user
    
    Args:
        user_id: User ID
        job_id: Job ID
        
    Returns:
        Success boolean
    """
    try:
        # Fetch job details
        jobs = await fetch_jobs(limit=1, job_id=job_id)
        
        if not jobs:
            logger.warning(f"Job {job_id} not found")
            return False
        
        job = jobs[0]
        
        # Save job in database
        from models.job import SavedJob
        
        async with get_db() as db:
            # Check if already saved
            result = await db.execute(
                select(SavedJob).where(
                    SavedJob.user_id == user_id,
                    SavedJob.job_id == job_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.info(f"Job {job_id} already saved for user {user_id}")
                return True
            
            # Create new saved job
            saved_job = SavedJob(
                user_id=user_id,
                job_id=job_id,
                job_data=job
            )
            
            db.add(saved_job)
            await db.commit()
            
            return True
    
    except Exception as e:
        logger.error(f"Error saving job: {str(e)}")
        return False