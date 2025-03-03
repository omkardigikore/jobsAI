# api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from utils.auth import get_admin_user

# Create router
router = APIRouter()

@router.get("/dashboard")
async def admin_dashboard(
    admin=Depends(get_admin_user)
):
    """
    Get admin dashboard data
    """
    # Get user stats
    from utils.db import get_db
    from sqlalchemy.future import select, func
    from models.user import User
    from models.subscription import Subscription
    from models.payment import Payment
    from models.resume import ResumeRequest
    from datetime import datetime, timedelta
    
    async with get_db() as db:
        # Total users
        users_result = await db.execute(select(func.count(User.id)))
        total_users = users_result.scalar()
        
        # Active subscriptions
        subs_result = await db.execute(
            select(func.count(Subscription.id))
            .where(
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow()
            )
        )
        active_subscriptions = subs_result.scalar()
        
        # Total revenue
        revenue_result = await db.execute(
            select(func.sum(Payment.amount))
            .where(Payment.status == "captured")
        )
        total_revenue = revenue_result.scalar() or 0
        
        # Recent users (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_users_result = await db.execute(
            select(func.count(User.id))
            .where(User.created_at >= seven_days_ago)
        )
        recent_users = recent_users_result.scalar()
        
        # Resume requests
        resume_requests_result = await db.execute(
            select(func.count(ResumeRequest.id))
        )
        total_resume_requests = resume_requests_result.scalar()
    
    return {
        "total_users": total_users,
        "active_subscriptions": active_subscriptions,
        "total_revenue": total_revenue / 100,  # Convert from paise to rupees
        "recent_users": recent_users,
        "total_resume_requests": total_resume_requests,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/broadcast")
async def broadcast_message(
    message: str,
    target: str,
    admin=Depends(get_admin_user)
):
    """
    Broadcast a message to users
    
    target can be:
    - "all": All users
    - "active": Users with active subscriptions
    - "expired": Users with expired subscriptions
    """
    from services.user_service import get_all_active_subscribers
    from services.notification_service import broadcast_message_to_users
    from utils.db import get_db
    from sqlalchemy.future import select
    from models.user import User
    from models.subscription import Subscription
    from datetime import datetime
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    # Get target users
    user_ids = []
    
    if target == "active":
        # Get users with active subscriptions
        active_users = await get_all_active_subscribers()
        user_ids = [user.id for user in active_users]
    
    elif target == "expired":
        # Get users with expired subscriptions
        async with get_db() as db:
            result = await db.execute(
                select(User.id)
                .join(
                    Subscription,
                    User.id == Subscription.user_id
                )
                .where(
                    Subscription.is_active == True,
                    Subscription.end_date <= datetime.utcnow()
                )
                .group_by(User.id)
            )
            
            user_ids = [row[0] for row in result.all()]
    
    else:  # "all"
        # Get all users
        async with get_db() as db:
            result = await db.execute(select(User.id))
            user_ids = [row[0] for row in result.all()]
    
    # Broadcast message
    results = await broadcast_message_to_users(user_ids, message)
    
    # Count successes and failures
    successes = sum(1 for success in results.values() if success)
    
    return {
        "message": "Broadcast sent",
        "target": target,
        "total_users": len(user_ids),
        "successes": successes,
        "failures": len(user_ids) - successes
    }


# # api/routes/admin.py
# from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from typing import List, Optional, Dict, Any
# from datetime import datetime, timedelta
# import json

# from utils.auth import get_admin_user
# from config.settings import BASE_DIR, ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY
# from utils.db import get_db
# from sqlalchemy.future import select, func
# from models.user import User
# from models.subscription import Subscription, SubscriptionPlan
# from models.payment import Payment
# from models.resume import ResumeRequest
# from models.job import SavedJob, JobListing

# # Create templates directory if using Jinja2 templates
# templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# router = APIRouter()

# # Admin authentication for web interface
# @router.post("/login")
# async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
#     """
#     Admin login endpoint for web interface
#     """
#     if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Invalid username or password"}
#         )
    
#     # Generate JWT token
#     from utils.auth import create_access_token
#     access_token = create_access_token(data={"sub": username, "is_admin": True})
    
#     # Set cookie and redirect to dashboard
#     response = templates.TemplateResponse(
#         "admin/dashboard.html",
#         {"request": request, "username": username}
#     )
#     response.set_cookie(
#         key="access_token", 
#         value=f"Bearer {access_token}",
#         httponly=True,
#         max_age=3600,  # 1 hour
#         expires=3600,  # 1 hour
#     )
    
#     return response

# @router.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     """Admin login page"""
#     return templates.TemplateResponse("admin/login.html", {"request": request})

# @router.get("/dashboard", response_class=HTMLResponse)
# async def admin_dashboard_page(request: Request):
#     """Admin dashboard page"""
#     # Extract token from cookie
#     token = request.cookies.get("access_token")
#     if not token or not token.startswith("Bearer "):
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Please log in"}
#         )
    
#     # Verify token
#     try:
#         from utils.auth import get_current_user
#         from fastapi.security import HTTPAuthorizationCredentials
#         user = get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token[7:]))
        
#         if not user.get("is_admin"):
#             return templates.TemplateResponse(
#                 "admin/login.html",
#                 {"request": request, "error": "Unauthorized"}
#             )
#     except:
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Session expired. Please log in again."}
#         )
    
#     # Get dashboard data
#     dashboard_data = await get_dashboard_data()
    
#     return templates.TemplateResponse(
#         "admin/dashboard.html",
#         {"request": request, "username": ADMIN_USERNAME, "data": dashboard_data}
#     )

# @router.get("/users", response_class=HTMLResponse)
# async def admin_users_page(request: Request):
#     """Admin users page"""
#     # Extract token from cookie
#     token = request.cookies.get("access_token")
#     if not token or not token.startswith("Bearer "):
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Please log in"}
#         )
    
#     # Verify token
#     try:
#         from utils.auth import get_current_user
#         from fastapi.security import HTTPAuthorizationCredentials
#         user = get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token[7:]))
        
#         if not user.get("is_admin"):
#             return templates.TemplateResponse(
#                 "admin/login.html",
#                 {"request": request, "error": "Unauthorized"}
#             )
#     except:
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Session expired. Please log in again."}
#         )
    
#     # Get users data
#     users = await get_all_users()
    
#     return templates.TemplateResponse(
#         "admin/users.html",
#         {"request": request, "username": ADMIN_USERNAME, "users": users}
#     )

# @router.get("/subscriptions", response_class=HTMLResponse)
# async def admin_subscriptions_page(request: Request):
#     """Admin subscriptions page"""
#     # Extract token from cookie
#     token = request.cookies.get("access_token")
#     if not token or not token.startswith("Bearer "):
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Please log in"}
#         )
    
#     # Verify token
#     try:
#         from utils.auth import get_current_user
#         from fastapi.security import HTTPAuthorizationCredentials
#         user = get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token[7:]))
        
#         if not user.get("is_admin"):
#             return templates.TemplateResponse(
#                 "admin/login.html",
#                 {"request": request, "error": "Unauthorized"}
#             )
#     except:
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Session expired. Please log in again."}
#         )
    
#     # Get subscriptions data
#     subscriptions = await get_all_subscriptions()
    
#     return templates.TemplateResponse(
#         "admin/subscriptions.html",
#         {"request": request, "username": ADMIN_USERNAME, "subscriptions": subscriptions}
#     )

# @router.get("/payments", response_class=HTMLResponse)
# async def admin_payments_page(request: Request):
#     """Admin payments page"""
#     # Extract token from cookie
#     token = request.cookies.get("access_token")
#     if not token or not token.startswith("Bearer "):
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Please log in"}
#         )
    
#     # Verify token
#     try:
#         from utils.auth import get_current_user
#         from fastapi.security import HTTPAuthorizationCredentials
#         user = get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token[7:]))
        
#         if not user.get("is_admin"):
#             return templates.TemplateResponse(
#                 "admin/login.html",
#                 {"request": request, "error": "Unauthorized"}
#             )
#     except:
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Session expired. Please log in again."}
#         )
    
#     # Get payments data
#     payments = await get_all_payments()
    
#     return templates.TemplateResponse(
#         "admin/payments.html",
#         {"request": request, "username": ADMIN_USERNAME, "payments": payments}
#     )

# @router.get("/support", response_class=HTMLResponse)
# async def admin_support_page(request: Request):
#     """Admin support page"""
#     # Extract token from cookie
#     token = request.cookies.get("access_token")
#     if not token or not token.startswith("Bearer "):
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Please log in"}
#         )
    
#     # Verify token
#     try:
#         from utils.auth import get_current_user
#         from fastapi.security import HTTPAuthorizationCredentials
#         user = get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token[7:]))
        
#         if not user.get("is_admin"):
#             return templates.TemplateResponse(
#                 "admin/login.html",
#                 {"request": request, "error": "Unauthorized"}
#             )
#     except:
#         return templates.TemplateResponse(
#             "admin/login.html",
#             {"request": request, "error": "Session expired. Please log in again."}
#         )
    
#     # In a real implementation, get support messages from database
#     # For now, return template with empty support messages
    
#     return templates.TemplateResponse(
#         "admin/support.html",
#         {"request": request, "username": ADMIN_USERNAME, "support_messages": []}
#     )

# # API Endpoints for admin dashboard
# @router.get("/dashboard")
# async def admin_dashboard(admin=Depends(get_admin_user)):
#     """
#     Get admin dashboard data
#     """
#     return await get_dashboard_data()

# async def get_dashboard_data():
#     """
#     Get dashboard data from database
#     """
#     try:
#         async with get_db() as db:
#             # Total users
#             result = await db.execute(select(func.count(User.id)))
#             total_users = result.scalar() or 0
            
#             # Active subscriptions
#             result = await db.execute(
#                 select(func.count(Subscription.id))
#                 .where(
#                     Subscription.is_active == True,
#                     Subscription.end_date > datetime.utcnow()
#                 )
#             )
#             active_subscriptions = result.scalar() or 0
            
#             # Total revenue
#             result = await db.execute(
#                 select(func.sum(Payment.amount))
#                 .where(Payment.status == "captured")
#             )
#             total_revenue = result.scalar() or 0
            
#             # Recent users (last 7 days)
#             seven_days_ago = datetime.utcnow() - timedelta(days=7)
#             result = await db.execute(
#                 select(func.count(User.id))
#                 .where(User.created_at >= seven_days_ago)
#             )
#             recent_users = result.scalar() or 0
            
#             # Monthly revenue
#             thirty_days_ago = datetime.utcnow() - timedelta(days=30)
#             result = await db.execute(
#                 select(func.sum(Payment.amount))
#                 .where(
#                     Payment.status == "captured",
#                     Payment.created_at >= thirty_days_ago
#                 )
#             )
#             monthly_revenue = result.scalar() or 0
            
#             # Recent payments (last 5)
#             result = await db.execute(
#                 select(Payment, User)
#                 .join(User, Payment.user_id == User.id)
#                 .where(Payment.status == "captured")
#                 .order_by(Payment.created_at.desc())
#                 .limit(5)
#             )
#             recent_payments = []
#             for payment, user in result.fetchall():
#                 recent_payments.append({
#                     "id": payment.id,
#                     "user": f"{user.first_name} {user.last_name or ''}".strip(),
#                     "email": user.email,
#                     "amount": payment.amount / 100,  # Convert paise to INR
#                     "date": payment.created_at.strftime("%Y-%m-%d %H:%M"),
#                     "status": payment.status
#                 })
            
#             # Recent users (last 5)
#             result = await db.execute(
#                 select(User)
#                 .order_by(User.created_at.desc())
#                 .limit(5)
#             )
#             recent_user_list = []
#             for user in result.scalars().all():
#                 recent_user_list.append({
#                     "id": user.id,
#                     "name": f"{user.first_name} {user.last_name or ''}".strip(),
#                     "email": user.email,
#                     "phone": user.phone,
#                     "date": user.created_at.strftime("%Y-%m-%d %H:%M")
#                 })
            
#             # Plan distribution
#             result = await db.execute(
#                 select(
#                     SubscriptionPlan.name, 
#                     func.count(Subscription.id)
#                 )
#                 .join(Subscription, SubscriptionPlan.id == Subscription.plan_id)
#                 .where(
#                     Subscription.is_active == True,
#                     Subscription.end_date > datetime.utcnow()
#                 )
#                 .group_by(SubscriptionPlan.name)
#             )
            
#             plan_distribution = {}
#             for plan_name, count in result.fetchall():
#                 plan_distribution[plan_name] = count
            
#             return {
#                 "total_users": total_users,
#                 "active_subscriptions": active_subscriptions,
#                 "total_revenue": total_revenue / 100,  # Convert paise to INR
#                 "recent_users": recent_users,
#                 "monthly_revenue": monthly_revenue / 100,  # Convert paise to INR
#                 "recent_payments": recent_payments,
#                 "recent_user_list": recent_user_list,
#                 "plan_distribution": plan_distribution
#             }
    
#     except Exception as e:
#         logger.error(f"Error getting dashboard data: {str(e)}")
#         return {
#             "total_users": 0,
#             "active_subscriptions": 0,
#             "total_revenue": 0,
#             "recent_users": 0,
#             "monthly_revenue": 0,
#             "recent_payments": [],
#             "recent_user_list": [],
#             "plan_distribution": {}
#         }

# @router.get("/api/users")
# async def admin_api_users(admin=Depends(get_admin_user)):
#     """
#     Get all users
#     """
#     return await get_all_users()

# async def get_all_users():
#     """
#     Get all users from database
#     """
#     try:
#         async with get_db() as db:
#             result = await db.execute(
#                 select(User)
#                 .order_by(User.created_at.desc())
#             )
            
#             users = []
#             for user in result.scalars().all():
#                 # Check if user has active subscription
#                 sub_result = await db.execute(
#                     select(Subscription)
#                     .where(
#                         Subscription.user_id == user.id,
#                         Subscription.is_active == True,
#                         Subscription.end_date > datetime.utcnow()
#                     )
#                 )
#                 subscription = sub_result.scalar_one_or_none()
                
#                 users.append({
#                     "id": user.id,
#                     "telegram_id": user.telegram_id,
#                     "username": user.username,
#                     "name": f"{user.first_name} {user.last_name or ''}".strip(),
#                     "email": user.email,
#                     "phone": user.phone,
#                     "city": user.city,
#                     "job_profile": user.job_profile,
#                     "is_active": user.is_active,
#                     "has_resume": user.has_resume,
#                     "has_subscription": subscription is not None,
#                     "created_at": user.created_at.strftime("%Y-%m-%d %H:%M")
#                 })
            
#             return users
    
#     except Exception as e:
#         logger.error(f"Error getting users: {str(e)}")
#         return []

# @router.get("/api/subscriptions")
# async def admin_api_subscriptions(admin=Depends(get_admin_user)):
#     """
#     Get all subscriptions
#     """
#     return await get_all_subscriptions()

# async def get_all_subscriptions():
#     """
#     Get all subscriptions from database
#     """
#     try:
#         async with get_db() as db:
#             result = await db.execute(
#                 select(Subscription, User, SubscriptionPlan)
#                 .join(User, Subscription.user_id == User.id)
#                 .join(SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id)
#                 .order_by(Subscription.created_at.desc())
#             )
            
#             subscriptions = []
#             for subscription, user, plan in result.fetchall():
#                 subscriptions.append({
#                     "id": subscription.id,
#                     "user": {
#                         "id": user.id,
#                         "name": f"{user.first_name} {user.last_name or ''}".strip(),
#                         "email": user.email
#                     },
#                     "plan": {
#                         "id": plan.id,
#                         "name": plan.name,
#                         "price": plan.price / 100  # Convert paise to INR
#                     },
#                     "start_date": subscription.start_date.strftime("%Y-%m-%d"),
#                     "end_date": subscription.end_date.strftime("%Y-%m-%d"),
#                     "is_active": subscription.is_active,
#                     "is_expired": subscription.end_date < datetime.utcnow(),
#                     "days_remaining": max(0, (subscription.end_date - datetime.utcnow()).days),
#                     "created_at": subscription.created_at.strftime("%Y-%m-%d %H:%M")
#                 })
            
#             return subscriptions
    
#     except Exception as e:
#         logger.error(f"Error getting subscriptions: {str(e)}")
#         return []

# @router.get("/api/payments")
# async def admin_api_payments(admin=Depends(get_admin_user)):
#     """
#     Get all payments
#     """
#     return await get_all_payments()

# async def get_all_payments():
#     """
#     Get all payments from database
#     """
#     try:
#         async with get_db() as db:
#             result = await db.execute(
#                 select(Payment, User)
#                 .join(User, Payment.user_id == User.id)
#                 .order_by(Payment.created_at.desc())
#             )
            
#             payments = []
#             for payment, user in result.fetchall():
#                 # Get subscription if exists
#                 subscription = None
#                 if payment.subscription_id:
#                     sub_result = await db.execute(
#                         select(Subscription, SubscriptionPlan)
#                         .join(SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id)
#                         .where(Subscription.id == payment.subscription_id)
#                     )
#                     sub_row = sub_result.fetchone()
#                     if sub_row:
#                         sub, plan = sub_row
#                         subscription = {
#                             "id": sub.id,
#                             "plan_name": plan.name,
#                             "start_date": sub.start_date.strftime("%Y-%m-%d"),
#                             "end_date": sub.end_date.strftime("%Y-%m-%d"),
#                             "is_active": sub.is_active
#                         }
                
#                 payments.append({
#                     "id": payment.id,
#                     "user": {
#                         "id": user.id,
#                         "name": f"{user.first_name} {user.last_name or ''}".strip(),
#                         "email": user.email
#                     },
#                     "amount": payment.amount / 100,  # Convert paise to INR
#                     "currency": payment.currency,
#                     "order_id": payment.order_id,
#                     "payment_id": payment.payment_id,
#                     "status": payment.status,
#                     "subscription": subscription,
#                     "created_at": payment.created_at.strftime("%Y-%m-%d %H:%M"),
#                     "updated_at": payment.updated_at.strftime("%Y-%m-%d %H:%M") if payment.updated_at else None
#                 })
            
#             return payments
    
#     except Exception as e:
#         logger.error(f"Error getting payments: {str(e)}")
#         return []

# @router.post("/broadcast")
# async def broadcast_message(
#     message: str,
#     target: str,
#     admin=Depends(get_admin_user)
# ):
#     """
#     Broadcast a message to users
    
#     target can be:
#     - "all": All users
#     - "active": Users with active subscriptions
#     - "expired": Users with expired subscriptions
#     """
#     from services.user_service import get_all_active_subscribers
#     from services.notification_service import broadcast_message_to_users
#     from utils.db import get_db
#     from sqlalchemy.future import select
#     from models.user import User
#     from models.subscription import Subscription
#     from datetime import datetime
    
#     if not message:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Message cannot be empty"
#         )
    
#     # Get target users
#     user_ids = []
    
#     if target == "active":
#         # Get users with active subscriptions
#         active_users = await get_all_active_subscribers()
#         user_ids = [user.id for user in active_users]
    
#     elif target == "expired":
#         # Get users with expired subscriptions
#         async with get_db() as db:
#             result = await db.execute(
#                 select(User.id)
#                 .join(
#                     Subscription,
#                     User.id == Subscription.user_id
#                 )
#                 .where(
#                     Subscription.is_active == True,
#                     Subscription.end_date <= datetime.utcnow()
#                 )
#                 .group_by(User.id)
#             )
            
#             user_ids = [row[0] for row in result.all()]
    
#     else:  # "all"
#         # Get all users
#         async with get_db() as db:
#             result = await db.execute(select(User.id))
#             user_ids = [row[0] for row in result.all()]
    
#     # Broadcast message
#     results = await broadcast_message_to_users(user_ids, message)
    
#     # Count successes and failures
#     successes = sum(1 for success in results.values() if success)
    
#     return {
#         "message": "Broadcast sent",
#         "target": target,
#         "total_users": len(user_ids),
#         "successes": successes,
#         "failures": len(user_ids) - successes
#     }