# services/subscription_service.py
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.subscription import Subscription, SubscriptionPlan
from utils.db import get_db

logger = logging.getLogger(__name__)

async def get_subscription_plans() -> List[SubscriptionPlan]:
    """
    Get all active subscription plans
    
    Returns:
        List of subscription plan objects
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(SubscriptionPlan)
                .where(SubscriptionPlan.is_active == True)
                .order_by(SubscriptionPlan.price)
            )
            
            return list(result.scalars().all())
    
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}")
        return []

async def get_subscription_plan_by_name(plan_name: str) -> Optional[SubscriptionPlan]:
    """
    Get a subscription plan by name
    
    Args:
        plan_name: Name of the plan
        
    Returns:
        Subscription plan object or None if not found
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(SubscriptionPlan)
                .where(SubscriptionPlan.name == plan_name)
            )
            
            return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Error getting subscription plan by name: {str(e)}")
        return None

async def get_subscription_plan_by_id(plan_id: int) -> Optional[SubscriptionPlan]:
    """
    Get a subscription plan by ID
    
    Args:
        plan_id: ID of the plan
        
    Returns:
        Subscription plan object or None if not found
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(SubscriptionPlan)
                .where(SubscriptionPlan.id == plan_id)
            )
            
            return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Error getting subscription plan by ID: {str(e)}")
        return None

async def get_user_active_subscription(user_id: int) -> Optional[Subscription]:
    """
    Get a user's active subscription
    
    Args:
        user_id: User ID
        
    Returns:
        Subscription object or None if no active subscription
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(Subscription)
                .where(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True,
                    Subscription.end_date > datetime.utcnow()
                )
                .order_by(Subscription.end_date.desc())
            )
            
            return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Error getting user active subscription: {str(e)}")
        return None

async def create_subscription(
    user_id: int,
    plan_id: int,
    duration_days: int,
    is_trial: bool = False
) -> Optional[Subscription]:
    """
    Create a new subscription for a user
    
    Args:
        user_id: User ID
        plan_id: Subscription plan ID
        duration_days: Duration in days
        is_trial: Whether this is a trial subscription
        
    Returns:
        Created subscription object or None if failed
    """
    try:
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=duration_days)
        
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            is_trial=is_trial,
            subscription_metadata={"source": "direct_creation"}
        )
        
        async with get_db() as db:
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)
            
            return subscription
    
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return None

async def extend_subscription(subscription_id: int, days: int) -> bool:
    """
    Extend a subscription by a number of days
    
    Args:
        subscription_id: Subscription ID
        days: Number of days to extend
        
    Returns:
        Success boolean
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(Subscription)
                .where(Subscription.id == subscription_id)
            )
            
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return False
            
            # If subscription already expired, extend from now
            if subscription.end_date < datetime.utcnow():
                subscription.end_date = datetime.utcnow() + timedelta(days=days)
            else:
                subscription.end_date = subscription.end_date + timedelta(days=days)
            
            # Make sure it's active
            subscription.is_active = True
            
            # Update metadata
            if not subscription.subscription_metadata:
                subscription.subscription_metadata = {}
            
            subscription.subscription_metadata.update({
                "extended_on": datetime.utcnow().isoformat(),
                "extended_days": days
            })
            
            await db.commit()
            return True
    
    except Exception as e:
        logger.error(f"Error extending subscription: {str(e)}")
        return False

async def cancel_subscription(subscription_id: int) -> bool:
    """
    Cancel a subscription
    
    Args:
        subscription_id: Subscription ID
        
    Returns:
        Success boolean
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(Subscription)
                .where(Subscription.id == subscription_id)
            )
            
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                logger.error(f"Subscription not found: {subscription_id}")
                return False
            
            subscription.is_active = False
            
            # Update metadata
            if not subscription.subscription_metadata:
                subscription.subscription_metadata = {}
            
            subscription.subscription_metadata.update({
                "cancelled_on": datetime.utcnow().isoformat(),
                "cancelled_reason": "user_request"
            })
            
            await db.commit()
            return True
    
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return False

async def get_expiring_subscriptions(days: int = 7) -> List[Subscription]:
    """
    Get subscriptions expiring within a number of days
    
    Args:
        days: Number of days threshold
        
    Returns:
        List of expiring subscription objects
    """
    try:
        now = datetime.utcnow()
        expiry_threshold = now + timedelta(days=days)
        
        async with get_db() as db:
            result = await db.execute(
                select(Subscription)
                .where(
                    Subscription.is_active == True,
                    Subscription.end_date > now,
                    Subscription.end_date <= expiry_threshold
                )
            )
            
            return list(result.scalars().all())
    
    except Exception as e:
        logger.error(f"Error getting expiring subscriptions: {str(e)}")
        return []