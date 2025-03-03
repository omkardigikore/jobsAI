#!/usr/bin/env python
# scripts/setup_db.py
import asyncio
import logging
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy_utils import database_exists, create_database

from config.settings import DATABASE_URL
from models.user import Base, User
from models.subscription import SubscriptionPlan, Subscription
from models.payment import Payment
from models.resume import ResumeRequest
from models.job import SavedJob, JobListing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create async engine with proper URI for creating database
sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

async def setup_database(drop_all=False):
    """Create database and tables"""
    try:
        # Create database if it doesn't exist
        if not database_exists(sync_url):
            create_database(sync_url)
            logger.info(f"Created database at {sync_url}")
        
        # Create tables
        engine = create_async_engine(DATABASE_URL)
        async with engine.begin() as conn:
            if drop_all:
                # Drop all tables if they exist
                logger.info("Dropping all existing tables...")
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("All tables dropped successfully")
            
            # Create all tables
            logger.info("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("All tables created successfully")
        
        # Initialize subscription plans
        await initialize_subscription_plans()
        
        logger.info("Database setup completed successfully")
    
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

async def initialize_subscription_plans():
    """Initialize subscription plans in the database"""
    try:
        from utils.db import get_db
        
        # Define default subscription plans
        plans = [
            {
                "name": "Basic",
                "description": "7-day subscription with 2 daily job updates and basic resume assistance",
                "price": 19900,  # ₹199 in paise
                "duration_days": 7,
                "features": {
                    "daily_updates": 2,
                    "resume_customization": True,
                    "support_priority": "normal"
                }
            },
            {
                "name": "Premium",
                "description": "30-day subscription with priority job updates and advanced resume customization",
                "price": 49900,  # ₹499 in paise
                "duration_days": 30,
                "features": {
                    "daily_updates": 3,
                    "resume_customization": True,
                    "support_priority": "high"
                }
            },
            {
                "name": "Professional",
                "description": "90-day subscription with premium job updates, unlimited resume customization, and interview prep",
                "price": 99900,  # ₹999 in paise
                "duration_days": 90,
                "features": {
                    "daily_updates": 5,
                    "resume_customization": True,
                    "support_priority": "highest",
                    "interview_prep": True
                }
            }
        ]
        
        # Add plans to database if they don't exist
        async with get_db() as db:
            for plan_data in plans:
                # Check if plan exists
                result = await db.execute(
                    select(SubscriptionPlan).where(SubscriptionPlan.name == plan_data["name"])
                )
                plan = result.scalar_one_or_none()
                
                if not plan:
                    plan = SubscriptionPlan(
                        name=plan_data["name"],
                        description=plan_data["description"],
                        price=plan_data["price"],
                        duration_days=plan_data["duration_days"],
                        features=plan_data["features"],
                        is_active=True
                    )
                    db.add(plan)
            
            await db.commit()
        
        logger.info("Successfully initialized subscription plans")
    
    except Exception as e:
        logger.error(f"Error initializing subscription plans: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting database setup")
    # Add command line argument to control dropping tables
    import argparse
    parser = argparse.ArgumentParser(description='Setup database tables')
    parser.add_argument('--drop', action='store_true', help='Drop all tables before creating them')
    args = parser.parse_args()
    
    asyncio.run(setup_database(drop_all=args.drop))