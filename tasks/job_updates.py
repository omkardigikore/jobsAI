# tasks/job_updates.py
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config.celery import app
from models.user import User
from models.subscription import Subscription
from services.job_service import get_personalized_jobs_for_user, format_job_for_telegram
from utils.db import get_db
from bot.bot import get_bot_instance

logger = logging.getLogger(__name__)

@app.task
def send_job_updates():
    """
    Celery task to send personalized job updates to subscribed users
    This is a wrapper that calls the async function
    """
    asyncio.run(_send_job_updates_async())

async def _send_job_updates_async():
    """
    Async implementation of the job updates task
    """
    logger.info("Starting job updates task")
    
    try:
        # Get all users with active subscriptions
        async with get_db() as db:
            # Join User and Subscription tables to get users with active subscriptions
            query = select(User).join(
                Subscription, 
                (User.id == Subscription.user_id) & 
                (Subscription.is_active == True) & 
                (Subscription.end_date > datetime.utcnow())
            ).filter(User.has_resume == True)
            
            result = await db.execute(query)
            users = result.scalars().all()
            
            logger.info(f"Found {len(users)} users with active subscriptions and resumes")
            
            # Send job updates to each user
            bot = get_bot_instance()
            
            for user in users:
                await process_user_job_updates(user, bot)
    
    except Exception as e:
        logger.error(f"Error in job updates task: {str(e)}")

async def process_user_job_updates(user: User, bot):
    """
    Process and send job updates for a specific user
    
    Args:
        user: User object
        bot: Telegram bot instance
    """
    try:
        # Get personalized jobs for user
        jobs, success = await get_personalized_jobs_for_user(user.id, limit=2)
        
        if not success or not jobs:
            logger.warning(f"No matched jobs found for user {user.id}")
            return
        
        logger.info(f"Sending {len(jobs)} job updates to user {user.id}")
        
        # Send each job as a separate message
        for job in jobs:
            # Format job for Telegram
            job_data = job.get("job_data", {})
            job_text = await format_job_for_telegram(job_data)
            
            # Add match percentage if available
            match_percentage = job.get("match_percentage")
            match_reasons = job.get("match_reasons")
            
            if match_percentage is not None:
                job_text = f"🔄 *Match: {match_percentage}%*\n\n" + job_text
            
            if match_reasons:
                job_text += f"\n\n*Why this matches your profile:*\n{match_reasons}"
            
            # Create inline keyboard with actions
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Customize Resume", callback_data=f"resume_request_{job_data.get('id')}")
                ],
                [
                    InlineKeyboardButton("Save Job", callback_data=f"save_job_{job_data.get('id')}"),
                    InlineKeyboardButton("Not Interested", callback_data=f"not_interested_{job_data.get('id')}")
                ]
            ])
            
            # Send message
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=job_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                
                # Add a small delay between messages to avoid rate limiting
                await asyncio.sleep(0.5)
            
            except Exception as send_error:
                logger.error(f"Error sending job update to user {user.id}: {str(send_error)}")
    
    except Exception as e:
        logger.error(f"Error processing job updates for user {user.id}: {str(e)}")

@app.task
def send_daily_job_digest():
    """
    Send a daily digest of top job matches to users
    This is typically scheduled to run once per day
    """
    asyncio.run(_send_daily_job_digest_async())

async def _send_daily_job_digest_async():
    """
    Async implementation of the daily job digest task
    """
    logger.info("Starting daily job digest task")
    
    try:
        # Get all users with active subscriptions and premium plans
        async with get_db() as db:
            # We'll only send the digest to premium and professional plan users
            query = select(User).join(
                Subscription, 
                (User.id == Subscription.user_id) & 
                (Subscription.is_active == True) & 
                (Subscription.end_date > datetime.utcnow())
            ).filter(User.has_resume == True)
            
            # Add plan filter if needed
            # .join(SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id)
            # .filter(SubscriptionPlan.name.in_(["Premium", "Professional"]))
            
            result = await db.execute(query)
            users = result.scalars().all()
            
            logger.info(f"Found {len(users)} users for daily job digest")
            
            # Send digest to each user
            bot = get_bot_instance()
            
            for user in users:
                await send_user_job_digest(user, bot)
    
    except Exception as e:
        logger.error(f"Error in daily job digest task: {str(e)}")

async def send_user_job_digest(user: User, bot):
    """
    Send a job digest to a specific user
    
    Args:
        user: User object
        bot: Telegram bot instance
    """
    try:
        # Get more personalized jobs for the digest
        jobs, success = await get_personalized_jobs_for_user(user.id, limit=5)
        
        if not success or not jobs:
            logger.warning(f"No matched jobs found for user {user.id} digest")
            return
        
        # Create digest message
        digest_text = (
            "📊 *Your Daily Job Matches*\n\n"
            "Here are today's top job matches based on your profile:\n\n"
        )
        
        for i, job in enumerate(jobs, 1):
            job_data = job.get("job_data", {})
            match_percentage = job.get("match_percentage", 0)
            
            digest_text += (
                f"*{i}. {job_data.get('title')}*\n"
                f"🏢 {job_data.get('company')}\n"
                f"📍 {job_data.get('location')}\n"
                f"🔄 Match: {match_percentage}%\n\n"
            )
        
        digest_text += "Click the button below to view these jobs in detail."
        
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("View Jobs", callback_data="view_job_digest")]
        ])
        
        # Send digest
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=digest_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        
        except Exception as send_error:
            logger.error(f"Error sending job digest to user {user.id}: {str(send_error)}")
    
    except Exception as e:
        logger.error(f"Error creating job digest for user {user.id}: {str(e)}")

@app.task
def update_job_database():
    """
    Update the local job database with fresh data from the API
    This task helps with faster job matching by keeping a local cache
    """
    asyncio.run(_update_job_database_async())

async def _update_job_database_async():
    """
    Async implementation of job database update task
    """
    logger.info("Starting job database update task")
    
    try:
        from services.job_service import fetch_jobs
        
        # Fetch latest jobs (with a high limit)
        jobs = await fetch_jobs(limit=200)
        
        if not jobs:
            logger.warning("No jobs returned from API for database update")
            return
        
        logger.info(f"Fetched {len(jobs)} jobs for database update")
        
        # Store jobs in database for quick access
        from models.job import JobListing
        
        async with get_db() as db:
            # Get existing job IDs to avoid duplicates
            from sqlalchemy import select
            result = await db.execute(select(JobListing.job_id))
            existing_job_ids = {row[0] for row in result.fetchall()}
            
            # Add new jobs
            new_job_count = 0
            
            for job in jobs:
                job_id = str(job.get("id"))
                
                if job_id not in existing_job_ids:
                    job_listing = JobListing(
                        job_id=job_id,
                        title=job.get("title"),
                        company=job.get("company"),
                        location=job.get("location"),
                        job_type=job.get("job_type"),
                        experience=job.get("experience"),
                        posted_date=job.get("posted_date"),
                        job_data=job
                    )
                    
                    db.add(job_listing)
                    new_job_count += 1
            
            # Commit if we have new jobs
            if new_job_count > 0:
                await db.commit()
                logger.info(f"Added {new_job_count} new jobs to database")
            else:
                logger.info("No new jobs to add to database")
            
            # Optionally, remove old jobs (e.g., older than 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # Use job posted_date if available, otherwise use created_at from our db
            delete_query = select(JobListing).filter(
                (JobListing.posted_date < thirty_days_ago) | 
                ((JobListing.posted_date == None) & (JobListing.created_at < thirty_days_ago))
            )
            
            result = await db.execute(delete_query)
            old_jobs = result.scalars().all()
            
            for old_job in old_jobs:
                await db.delete(old_job)
            
            if old_jobs:
                await db.commit()
                logger.info(f"Removed {len(old_jobs)} old jobs from database")
    
    except Exception as e:
        logger.error(f"Error updating job database: {str(e)}")