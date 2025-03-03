# tasks/subscription_alerts.py
import logging
import asyncio
from datetime import datetime, timedelta

from sqlalchemy.future import select
from config.celery import app
from models.user import User
from models.subscription import Subscription
from services.notification_service import (
    send_subscription_expiry_reminder,
    send_subscription_expired_notification
)
from utils.db import get_db

logger = logging.getLogger(__name__)

@app.task
def check_expiring_subscriptions():
    """
    Celery task to check for expiring subscriptions and send reminders
    This is a wrapper that calls the async function
    """
    asyncio.run(_check_expiring_subscriptions_async())

async def _check_expiring_subscriptions_async():
    """
    Async implementation of the subscription check task
    """
    logger.info("Starting subscription expiry check task")
    
    try:
        async with get_db() as db:
            now = datetime.utcnow()
            
            # Check for subscriptions expiring in 7 days
            seven_days_from_now = now + timedelta(days=7)
            
            reminder_query = select(User, Subscription).join(
                Subscription,
                User.id == Subscription.user_id
            ).where(
                Subscription.is_active == True,
                Subscription.end_date > now,
                Subscription.end_date <= seven_days_from_now
            )
            
            result = await db.execute(reminder_query)
            expiring_soon = result.all()
            
            logger.info(f"Found {len(expiring_soon)} subscriptions expiring within 7 days")
            
            # Send reminders based on days remaining
            for user, subscription in expiring_soon:
                days_left = (subscription.end_date - now).days
                
                # Send different reminders based on time left
                if days_left == 7:
                    # 7-day reminder
                    await send_subscription_expiry_reminder(
                        user.telegram_id,
                        days_left,
                        subscription.id
                    )
                    logger.info(f"Sent 7-day reminder to user {user.id}")
                
                elif days_left == 3:
                    # 3-day reminder
                    await send_subscription_expiry_reminder(
                        user.telegram_id,
                        days_left,
                        subscription.id
                    )
                    logger.info(f"Sent 3-day reminder to user {user.id}")
                
                elif days_left == 1:
                    # 1-day reminder
                    await send_subscription_expiry_reminder(
                        user.telegram_id,
                        days_left,
                        subscription.id
                    )
                    logger.info(f"Sent 1-day reminder to user {user.id}")
            
            # Check for subscriptions that just expired (within the last 24 hours)
            yesterday = now - timedelta(days=1)
            
            expired_query = select(User, Subscription).join(
                Subscription,
                User.id == Subscription.user_id
            ).where(
                Subscription.is_active == True,
                Subscription.end_date > yesterday,
                Subscription.end_date <= now
            )
            
            result = await db.execute(expired_query)
            just_expired = result.all()
            
            logger.info(f"Found {len(just_expired)} subscriptions that just expired")
            
            # Send expiration notifications and deactivate subscriptions
            for user, subscription in just_expired:
                # Send expiration notification
                await send_subscription_expired_notification(
                    user.telegram_id,
                    subscription.id
                )
                
                # Deactivate subscription
                subscription.is_active = False
                
                logger.info(f"Deactivated expired subscription for user {user.id}")
            
            # Commit changes if any subscriptions were deactivated
            if just_expired:
                await db.commit()
    
    except Exception as e:
        logger.error(f"Error checking expiring subscriptions: {str(e)}")

@app.task
def process_renewal_requests():
    """
    Process subscription renewal requests
    """
    asyncio.run(_process_renewal_requests_async())

async def _process_renewal_requests_async():
    """
    Async implementation of renewal processing
    """
    logger.info("Starting renewal requests processing task")
    
    try:
        from models.payment import Payment
        
        async with get_db() as db:
            # Find payments for renewals that are completed but subscription not yet renewed
            query = select(Payment).join(
                Subscription,
                Payment.subscription_id == Subscription.id
            ).where(
                Payment.status == "captured",
                Subscription.is_active == False,
                Subscription.end_date < datetime.utcnow()
            )
            
            result = await db.execute(query)
            renewal_payments = result.scalars().all()
            
            logger.info(f"Found {len(renewal_payments)} pending renewal payments")
            
            for payment in renewal_payments:
                try:
                    # Get the old subscription
                    old_sub_query = select(Subscription).where(Subscription.id == payment.subscription_id)
                    old_sub_result = await db.execute(old_sub_query)
                    old_subscription = old_sub_result.scalar_one_or_none()
                    
                    if not old_subscription:
                        logger.error(f"Old subscription not found for payment {payment.id}")
                        continue
                    
                    # Create new subscription
                    from datetime import datetime
                    start_date = datetime.utcnow()
                    
                    # Get subscription plan
                    from models.subscription import SubscriptionPlan
                    plan_query = select(SubscriptionPlan).where(SubscriptionPlan.id == old_subscription.plan_id)
                    plan_result = await db.execute(plan_query)
                    plan = plan_result.scalar_one_or_none()
                    
                    if not plan:
                        logger.error(f"Subscription plan not found for old subscription {old_subscription.id}")
                        continue
                    
                    end_date = start_date + timedelta(days=plan.duration_days)
                    
                    new_subscription = Subscription(
                        user_id=payment.user_id,
                        plan_id=plan.id,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=True,
                        is_trial=False,
                        subscription_metadata={"renewed_from": old_subscription.id}
                    )
                    
                    db.add(new_subscription)
                    await db.flush()
                    
                    # Update payment with new subscription ID
                    payment.subscription_id = new_subscription.id
                    
                    # Notify user
                    from services.notification_service import send_payment_success_notification
                    
                    # Get user's telegram ID
                    user_query = select(User).where(User.id == payment.user_id)
                    user_result = await db.execute(user_query)
                    user = user_result.scalar_one_or_none()
                    
                    if user:
                        await send_payment_success_notification(
                            user.telegram_id,
                            new_subscription.id
                        )
                
                except Exception as e:
                    logger.error(f"Error processing renewal payment {payment.id}: {str(e)}")
            
            # Commit all changes
            if renewal_payments:
                await db.commit()
    
    except Exception as e:
        logger.error(f"Error processing renewal requests: {str(e)}")