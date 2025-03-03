# api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from models.user import User
from services.user_service import get_user_by_id, get_all_active_subscribers
from utils.auth import get_admin_user

# Create router
router = APIRouter()

@router.get("/")
async def get_users(
    admin=Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
):
    """
    Get list of users (admin only)
    """
    # This is a placeholder - you would implement this with your user service
    from utils.db import get_db
    from sqlalchemy.future import select
    
    async with get_db() as db:
        query = select(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Convert to dict for JSON response
        return [
            {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "is_active": user.is_active,
                "has_resume": user.has_resume
            }
            for user in users
        ]

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    admin=Depends(get_admin_user)
):
    """
    Get user by ID (admin only)
    """
    user = await get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get subscription info
    from services.user_service import get_user_subscription_details
    has_subscription, subscription_details = await get_user_subscription_details(user_id)
    
    # Convert to dict for JSON response
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "is_active": user.is_active,
        "has_resume": user.has_resume,
        "subscription": subscription_details if has_subscription else None
    }

@router.get("/stats/active")
async def get_active_users_stats(
    admin=Depends(get_admin_user)
):
    """
    Get statistics about active users (admin only)
    """
    # Get active subscribers
    active_subscribers = await get_all_active_subscribers()
    
    # Count users with resumes
    users_with_resume = sum(1 for user in active_subscribers if user.has_resume)
    
    return {
        "total_active_subscribers": len(active_subscribers),
        "users_with_resume": users_with_resume,
        "users_without_resume": len(active_subscribers) - users_with_resume,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    admin=Depends(get_admin_user)
):
    """
    Deactivate a user (admin only)
    """
    from utils.db import get_db
    
    user = await get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    async with get_db() as db:
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await db.commit()
    
    return {"message": f"User {user_id} deactivated successfully"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    admin=Depends(get_admin_user)
):
    """
    Activate a user (admin only)
    """
    from utils.db import get_db
    
    user = await get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    async with get_db() as db:
        user.is_active = True
        user.updated_at = datetime.utcnow()
        await db.commit()
    
    return {"message": f"User {user_id} activated successfully"}