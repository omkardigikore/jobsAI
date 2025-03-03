# services/payment_service.py
import logging
import json
from datetime import datetime, timedelta
import razorpay
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, WEBHOOK_URL
from models.user import User
from models.subscription import Subscription, SubscriptionPlan
from models.payment import Payment
from utils.db import get_db

logger = logging.getLogger(__name__)

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Subscription plan details
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "days": 7,
        "amount": 19900,  # in paise (₹199)
        "description": "7-day subscription with 2 daily job updates and basic resume assistance"
    },
    "premium": {
        "name": "Premium",
        "days": 30,
        "amount": 49900,  # in paise (₹499)
        "description": "30-day subscription with priority job updates and advanced resume customization"
    },
    "professional": {
        "name": "Professional",
        "days": 90,
        "amount": 99900,  # in paise (₹999)
        "description": "90-day subscription with premium job updates, unlimited resume customization, and interview prep"
    }
}

async def generate_payment_link(user_id: int, plan_type: str, email: str) -> tuple:
    """
    Generate a Razorpay payment link for a subscription
    
    Args:
        user_id: Database user ID
        plan_type: Subscription plan type (basic, premium, professional)
        email: User's email address
        
    Returns:
        tuple: (payment_link_url, order_id)
    """
    try:
        # Get plan details
        plan = SUBSCRIPTION_PLANS.get(plan_type)
        if not plan:
            raise ValueError(f"Invalid subscription plan: {plan_type}")
        
        # Get user details
        async with get_db() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError(f"User not found: {user_id}")
            
            # Create order data
            receipt_id = f"receipt_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            notes = {
                "user_id": str(user_id),
                "plan_type": plan_type,
                "telegram_id": str(user.telegram_id)
            }
            
            # Create Razorpay order
            order_data = {
                "amount": plan["amount"],
                "currency": "INR",
                "receipt": receipt_id,
                "notes": notes,
                "payment_capture": 1  # Auto-capture payment
            }
            
            order = client.order.create(order_data)
            order_id = order["id"]
            
            # Create payment record in database
            new_payment = Payment(
                user_id=user_id,
                amount=plan["amount"],
                order_id=order_id,
                status="created",
                payment_details=order
            )
            
            db.add(new_payment)
            await db.commit()
            
            # Generate payment link
            payment_link_data = {
                "amount": plan["amount"],
                "currency": "INR",
                "accept_partial": False,
                "description": f"{plan['name']} Subscription - Job Updates Bot",
                "customer": {
                    "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                    "email": email,
                    "contact": user.phone or "+910000000000"  # Default phone if not available
                },
                "notify": {
                    "email": True,
                    "sms": True
                },
                "reminder_enable": True,
                "notes": notes,
                # "callback_url": f"{WEBHOOK_URL}/payment/callback?order_id={order_id}",
                "callback_url": f"{WEBHOOK_URL}/api/v1/payments/webhook/razorpay?order_id={order_id}",
                # "callback_url": f"{WEBHOOK_URL.rstrip('/')}?order_id={order_id}",
                "callback_method": "get"
            }
            
            # Create payment link
            payment_link = client.payment_link.create(payment_link_data)
            
            return payment_link["short_url"], order_id
    
    except Exception as e:
        logger.error(f"Error generating payment link: {str(e)}")
        raise

async def verify_payment_status(user_id: int, order_id: str) -> Subscription:
    """
    Verify the payment status for an order and create subscription if payment is successful
    
    Args:
        user_id: Database user ID
        order_id: Razorpay order ID
        
    Returns:
        Subscription object if payment successful, None otherwise
    """
    try:
        # Get payment details from Razorpay
        order = client.order.fetch(order_id)
        
        # Check if payment is successful
        if order["status"] != "paid":
            logger.info(f"Order {order_id} not paid yet. Status: {order['status']}")
            return None
        
        # Update payment status in database
        async with get_db() as db:
            # Get payment record
            result = await db.execute(
                select(Payment).where(
                    Payment.order_id == order_id,
                    Payment.user_id == user_id
                )
            )
            payment = result.scalar_one_or_none()
            
            if not payment:
                logger.error(f"Payment record not found for order {order_id}")
                return None
            
            # Update payment status
            payment.status = "captured"
            payment.payment_id = order.get("payment_id")
            payment.payment_details = order
            
            # Get plan type from payment notes
            plan_type = order["notes"].get("plan_type")
            if not plan_type or plan_type not in SUBSCRIPTION_PLANS:
                logger.error(f"Invalid plan type in order notes: {plan_type}")
                return None
            
            plan_data = SUBSCRIPTION_PLANS[plan_type]
            
            # Get or create subscription plan
            result = await db.execute(
                select(SubscriptionPlan).where(SubscriptionPlan.name == plan_data["name"])
            )
            subscription_plan = result.scalar_one_or_none()
            
            if not subscription_plan:
                subscription_plan = SubscriptionPlan(
                    name=plan_data["name"],
                    description=plan_data["description"],
                    price=plan_data["amount"],
                    duration_days=plan_data["days"],
                    features={"daily_updates": 2}
                )
                db.add(subscription_plan)
                await db.flush()
            
            # Create subscription
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=plan_data["days"])
            
            subscription = Subscription(
                user_id=user_id,
                plan_id=subscription_plan.id,
                start_date=start_date,
                end_date=end_date,
                is_active=True,
                subscription_metadata={"source": "razorpay_payment"}
            )
            
            db.add(subscription)
            
            # Link payment to subscription
            payment.subscription_id = subscription.id
            
            await db.commit()
            
            return subscription
    
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return None

async def process_razorpay_webhook(webhook_data: dict):
    """
    Process Razorpay webhook events
    
    Args:
        webhook_data: Webhook payload from Razorpay
    """
    try:
        event = webhook_data.get("event")
        
        if not event:
            logger.error("Invalid webhook data: event missing")
            return
        
        payload = webhook_data.get("payload", {}).get("payment", {}).get("entity", {})
        
        if not payload:
            logger.error("Invalid webhook data: payload missing")
            return
        
        order_id = payload.get("order_id")
        payment_id = payload.get("id")
        
        if not order_id:
            logger.error("Invalid webhook data: order_id missing")
            return
        
        # Handle different event types
        if event == "payment.authorized":
            await _handle_payment_authorized(order_id, payment_id, payload)
        elif event == "payment.failed":
            await _handle_payment_failed(order_id, payment_id, payload)
        elif event == "refund.created":
            await _handle_refund_created(order_id, payment_id, payload)
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")

async def _handle_payment_authorized(order_id: str, payment_id: str, payload: dict):
    """Handle payment.authorized webhook event"""
    try:
        async with get_db() as db:
            # Find payment record
            result = await db.execute(select(Payment).where(Payment.order_id == order_id))
            payment = result.scalar_one_or_none()
            
            if not payment:
                logger.error(f"Payment record not found for order {order_id}")
                return
            
            # Update payment status
            payment.status = "captured"
            payment.payment_id = payment_id
            payment.payment_details = payload
            
            # If we don't have a subscription yet, create one
            if not payment.subscription_id:
                user_id = payment.user_id
                notes = payload.get("notes", {})
                plan_type = notes.get("plan_type")
                
                if not plan_type or plan_type not in SUBSCRIPTION_PLANS:
                    logger.error(f"Invalid plan type in payment notes: {plan_type}")
                    return
                
                plan_data = SUBSCRIPTION_PLANS[plan_type]
                
                # Get or create subscription plan
                result = await db.execute(
                    select(SubscriptionPlan).where(SubscriptionPlan.name == plan_data["name"])
                )
                subscription_plan = result.scalar_one_or_none()
                
                if not subscription_plan:
                    subscription_plan = SubscriptionPlan(
                        name=plan_data["name"],
                        description=plan_data["description"],
                        price=plan_data["amount"],
                        duration_days=plan_data["days"],
                        features={"daily_updates": 2}
                    )
                    db.add(subscription_plan)
                    await db.flush()
                
                # Create subscription
                start_date = datetime.utcnow()
                end_date = start_date + timedelta(days=plan_data["days"])
                
                subscription = Subscription(
                    user_id=user_id,
                    plan_id=subscription_plan.id,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True
                )
                
                db.add(subscription)
                await db.flush()
                
                # Link payment to subscription
                payment.subscription_id = subscription.id
            
            await db.commit()
            
            # Send notification to user about successful payment
            from services.notification_service import send_payment_success_notification
            telegram_id = int(payload.get("notes", {}).get("telegram_id", 0))
            
            if telegram_id:
                await send_payment_success_notification(telegram_id, payment.subscription_id)
    
    except Exception as e:
        logger.error(f"Error handling payment authorized: {str(e)}")

async def _handle_payment_failed(order_id: str, payment_id: str, payload: dict):
    """Handle payment.failed webhook event"""
    try:
        async with get_db() as db:
            # Find payment record
            result = await db.execute(select(Payment).where(Payment.order_id == order_id))
            payment = result.scalar_one_or_none()
            
            if not payment:
                logger.error(f"Payment record not found for order {order_id}")
                return
            
            # Update payment status
            payment.status = "failed"
            payment.payment_id = payment_id
            payment.payment_details = payload
            
            await db.commit()
            
            # Send notification to user about failed payment
            from services.notification_service import send_payment_failed_notification
            telegram_id = int(payload.get("notes", {}).get("telegram_id", 0))
            
            if telegram_id:
                await send_payment_failed_notification(telegram_id, order_id)
    
    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")

async def _handle_refund_created(order_id: str, payment_id: str, payload: dict):
    """Handle refund.created webhook event"""
    try:
        async with get_db() as db:
            # Find payment record
            result = await db.execute(select(Payment).where(
                (Payment.order_id == order_id) | (Payment.payment_id == payment_id)
            ))
            payment = result.scalar_one_or_none()
            
            if not payment:
                logger.error(f"Payment record not found for order {order_id} or payment {payment_id}")
                return
            
            # Update payment status
            payment.status = "refunded"
            payment.payment_details = {**payment.payment_details, "refund": payload}
            
            # Deactivate subscription if exists
            if payment.subscription_id:
                result = await db.execute(select(Subscription).where(
                    Subscription.id == payment.subscription_id
                ))
                subscription = result.scalar_one_or_none()
                
                if subscription:
                    subscription.is_active = False
            
            await db.commit()
            
            # Send notification to user about refund
            from services.notification_service import send_refund_notification
            telegram_id = int(payload.get("notes", {}).get("telegram_id", 0))
            
            if telegram_id:
                await send_refund_notification(telegram_id, payment.id)
    
    except Exception as e:
        logger.error(f"Error handling refund created: {str(e)}")