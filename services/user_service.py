# services/user_service.py
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from sqlalchemy import update, and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.subscription import Subscription
from utils.db import get_db, get_or_create

logger = logging.getLogger(__name__)

async def get_or_create_user(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None
) -> User:
    """
    Get a user by Telegram ID or create a new one if not found
    
    Args:
        telegram_id: User's Telegram ID
        username: User's Telegram username
        first_name: User's first name
        last_name: User's last name
        email: User's email address
        phone: User's phone number
        
    Returns:
        User object
    """
    try:
        async with get_db() as db:
            # Try to find the user
            result = await db.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Update user info if it has changed
                update_fields = {}
                if username and username != user.username:
                    update_fields["username"] = username
                if first_name and first_name != user.first_name:
                    update_fields["first_name"] = first_name
                if last_name and last_name != user.last_name:
                    update_fields["last_name"] = last_name
                if email and email != user.email:
                    update_fields["email"] = email
                if phone and phone != user.phone:
                    update_fields["phone"] = phone
                
                if update_fields:
                    for field, value in update_fields.items():
                        setattr(user, field, value)
                    
                    user.updated_at = datetime.utcnow()
                    await db.commit()
                
                return user
            else:
                # Create new user
                new_user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone
                )
                
                db.add(new_user)
                await db.commit()
                await db.refresh(new_user)
                
                logger.info(f"Created new user with telegram_id {telegram_id}")
                return new_user
    
    except Exception as e:
        logger.error(f"Error in get_or_create_user: {str(e)}")
        raise

async def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Get a user by database ID
    
    Args:
        user_id: User's database ID
        
    Returns:
        User object or None if not found
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Error in get_user_by_id: {str(e)}")
        return None

async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """
    Get a user by Telegram ID
    
    Args:
        telegram_id: User's Telegram ID
        
    Returns:
        User object or None if not found
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Error in get_user_by_telegram_id: {str(e)}")
        return None

async def update_user_email(user_id: int, email: str) -> bool:
    """
    Update a user's email address
    
    Args:
        user_id: User's database ID
        email: New email address
        
    Returns:
        Success boolean
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False
            
            user.email = email
            user.updated_at = datetime.utcnow()
            
            await db.commit()
            return True
    
    except Exception as e:
        logger.error(f"Error in update_user_email: {str(e)}")
        return False

async def update_user_phone(user_id: int, phone: str) -> bool:
    """
    Update a user's phone number
    
    Args:
        user_id: User's database ID
        phone: New phone number
        
    Returns:
        Success boolean
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False
            
            user.phone = phone
            user.updated_at = datetime.utcnow()
            
            await db.commit()
            return True
    
    except Exception as e:
        logger.error(f"Error in update_user_phone: {str(e)}")
        return False

async def update_user_resume_status(
    user_id: int,
    has_resume: bool,
    resume_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Update a user's resume status and data
    
    Args:
        user_id: User's database ID
        has_resume: Whether the user has a resume
        resume_data: Parsed resume data (optional)
        
    Returns:
        Success boolean
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False
            
            user.has_resume = has_resume
            
            if resume_data:
                user.resume_data = resume_data
            
            user.updated_at = datetime.utcnow()
            
            await db.commit()
            return True
    
    except Exception as e:
        logger.error(f"Error in update_user_resume_status: {str(e)}")
        return False

async def check_user_subscription(user_id: int) -> bool:
    """
    Check if a user has an active subscription
    
    Args:
        user_id: User's database ID
        
    Returns:
        Boolean indicating if user has active subscription
    """
    try:
        async with get_db() as db:
            # Check for active subscription that hasn't expired
            result = await db.execute(
                select(Subscription).where(
                    and_(
                        Subscription.user_id == user_id,
                        Subscription.is_active == True,
                        Subscription.end_date > datetime.utcnow()
                    )
                )
            )
            subscription = result.scalar_one_or_none()
            
            return subscription is not None
    
    except Exception as e:
        logger.error(f"Error in check_user_subscription: {str(e)}")
        return False

async def get_user_subscription_details(user_id: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Get details about a user's subscription
    
    Args:
        user_id: User's database ID
        
    Returns:
        Tuple of (has_active_subscription, subscription_details)
    """
    try:
        async with get_db() as db:
            # Join Subscription with SubscriptionPlan
            from sqlalchemy.orm import joinedload
            from models.subscription import SubscriptionPlan
            
            query = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True,
                    Subscription.end_date > datetime.utcnow()
                )
            ).options(
                joinedload(Subscription.plan)
            ).order_by(
                Subscription.end_date.desc()
            )
            
            result = await db.execute(query)
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                return False, None
            
            # Calculate days remaining
            days_remaining = (subscription.end_date - datetime.utcnow()).days
            
            subscription_details = {
                "subscription_id": subscription.id,
                "plan_name": subscription.plan.name,
                "start_date": subscription.start_date.strftime("%Y-%m-%d"),
                "end_date": subscription.end_date.strftime("%Y-%m-%d"),
                "days_remaining": max(0, days_remaining),
                "features": subscription.plan.features
            }
            
            return True, subscription_details
    
    except Exception as e:
        logger.error(f"Error in get_user_subscription_details: {str(e)}")
        return False, None

async def deactivate_user_subscription(subscription_id: int) -> bool:
    """
    Deactivate a user's subscription
    
    Args:
        subscription_id: Subscription ID
        
    Returns:
        Success boolean
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(Subscription).where(Subscription.id == subscription_id)
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                logger.warning(f"Subscription not found: {subscription_id}")
                return False
            
            subscription.is_active = False
            subscription.updated_at = datetime.utcnow()
            
            await db.commit()
            return True
    
    except Exception as e:
        logger.error(f"Error in deactivate_user_subscription: {str(e)}")
        return False

async def get_all_active_subscribers() -> list:
    """
    Get all users with active subscriptions
    
    Returns:
        List of users with active subscriptions
    """
    try:
        async with get_db() as db:
            # Join User and Subscription
            query = select(User).join(
                Subscription, 
                and_(
                    User.id == Subscription.user_id,
                    Subscription.is_active == True,
                    Subscription.end_date > datetime.utcnow()
                )
            )
            
            result = await db.execute(query)
            users = result.scalars().all()
            
            return list(users)
    
    except Exception as e:
        logger.error(f"Error in get_all_active_subscribers: {str(e)}")
        return []