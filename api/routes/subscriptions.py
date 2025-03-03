# api/routes/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from utils.auth import get_admin_user
from services.subscription_service import get_subscription_plans, get_expiring_subscriptions

# Create router
router = APIRouter()

@router.get("/plans")
async def get_plans():
    """
    Get all subscription plans
    """
    plans = await get_subscription_plans()
    
    return [
        {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "price": plan.price / 100,  # Convert from paise to rupees
            "duration_days": plan.duration_days,
            "features": plan.features
        }
        for plan in plans
    ]

@router.get("/expiring")
async def get_expiring_subscriptions_api(
    days: int = 7,
    admin=Depends(get_admin_user)
):
    """
    Get subscriptions expiring within the given days (admin only)
    """
    expiring = await get_expiring_subscriptions(days)
    
    # Join with user data
    from utils.db import get_db
    from sqlalchemy.future import select
    from models.user import User
    
    result = []
    
    async with get_db() as db:
        for subscription in expiring:
            user_result = await db.execute(
                select(User).where(User.id == subscription.user_id)
            )
            
            user = user_result.scalar_one_or_none()
            
            if user:
                result.append({
                    "subscription_id": subscription.id,
                    "user_id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                    "email": user.email,
                    "plan_name": subscription.plan.name if subscription.plan else None,
                    "end_date": subscription.end_date.isoformat(),
                    "days_remaining": subscription.days_remaining
                })
    
    return result



