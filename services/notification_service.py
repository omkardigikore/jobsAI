# services/notification_service.py
import logging
import asyncio
from typing import Optional, Dict, Any, Union, List
from datetime import datetime
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from config.settings import TELEGRAM_BOT_TOKEN
from bot.bot import get_bot_instance

logger = logging.getLogger(__name__)

async def send_telegram_message(
    telegram_id: int,
    text: str,
    parse_mode: str = "Markdown",
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    disable_web_page_preview: bool = False
) -> bool:
    """
    Send a message to a user via Telegram
    
    Args:
        telegram_id: User's Telegram ID
        text: Message text
        parse_mode: Parse mode (Markdown or HTML)
        reply_markup: Optional inline keyboard markup
        disable_web_page_preview: Whether to disable web page preview
        
    Returns:
        Success boolean
    """
    try:
        bot = get_bot_instance()
        
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview
        )
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending Telegram message to {telegram_id}: {str(e)}")
        return False

async def send_payment_success_notification(telegram_id: int, subscription_id: int) -> bool:
    """
    Send notification about successful payment
    
    Args:
        telegram_id: User's Telegram ID
        subscription_id: Subscription ID
        
    Returns:
        Success boolean
    """
    try:
        # Get subscription details
        from services.user_service import get_user_subscription_details
        from models.user import User
        from utils.db import get_db
        from sqlalchemy.future import select
        
        async with get_db() as db:
            result = await db.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User not found with telegram_id {telegram_id}")
                return False
            
            has_subscription, subscription_details = await get_user_subscription_details(user.id)
            
            if not has_subscription or not subscription_details:
                logger.error(f"Subscription details not found for user {user.id}")
                return False
            
            # Create notification message
            message = (
                f"🎉 *Payment Successful!*\n\n"
                f"Your payment has been confirmed and your subscription is now active.\n\n"
                f"*Subscription Details:*\n"
                f"• Plan: {subscription_details['plan_name']}\n"
                f"• Start Date: {subscription_details['start_date']}\n"
                f"• End Date: {subscription_details['end_date']}\n"
                f"• Days Remaining: {subscription_details['days_remaining']}\n\n"
            )
            
            # Add next steps based on resume status
            if user.has_resume:
                message += (
                    "You'll now start receiving personalized job updates based on your resume. "
                    "Watch for the first update soon!"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("View Jobs", callback_data="my_jobs")],
                    [InlineKeyboardButton("Main Menu", callback_data="back_to_main")]
                ])
            else:
                message += (
                    "To start receiving personalized job updates, please upload your resume. "
                    "This will help us match you with the most relevant opportunities."
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
                    [InlineKeyboardButton("Main Menu", callback_data="back_to_main")]
                ])
            
            # Send notification
            return await send_telegram_message(
                telegram_id=telegram_id,
                text=message,
                reply_markup=keyboard
            )
    
    except Exception as e:
        logger.error(f"Error sending payment success notification: {str(e)}")
        return False

async def send_payment_failed_notification(telegram_id: int, order_id: str) -> bool:
    """
    Send notification about failed payment
    
    Args:
        telegram_id: User's Telegram ID
        order_id: Razorpay order ID
        
    Returns:
        Success boolean
    """
    try:
        message = (
            "❌ *Payment Failed*\n\n"
            "We were unable to process your payment. This could be due to:\n"
            "• Insufficient funds\n"
            "• Card declined by bank\n"
            "• Network/connectivity issues\n\n"
            "You can try again with a different payment method or contact your bank for assistance."
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Try Again", callback_data="subscription")],
            [InlineKeyboardButton("Contact Support", callback_data="support")]
        ])
        
        return await send_telegram_message(
            telegram_id=telegram_id,
            text=message,
            reply_markup=keyboard
        )
    
    except Exception as e:
        logger.error(f"Error sending payment failed notification: {str(e)}")
        return False

async def send_refund_notification(telegram_id: int, payment_id: int) -> bool:
    """
    Send notification about refund
    
    Args:
        telegram_id: User's Telegram ID
        payment_id: Payment ID
        
    Returns:
        Success boolean
    """
    try:
        message = (
            "💰 *Refund Processed*\n\n"
            "Your refund has been processed successfully. The amount will be credited to your "
            "original payment method. This may take 5-7 business days depending on your bank.\n\n"
            "If you have any questions about the refund, please contact our support team."
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Support", callback_data="support")],
            [InlineKeyboardButton("Main Menu", callback_data="back_to_main")]
        ])
        
        return await send_telegram_message(
            telegram_id=telegram_id,
            text=message,
            reply_markup=keyboard
        )
    
    except Exception as e:
        logger.error(f"Error sending refund notification: {str(e)}")
        return False

async def send_resume_notification(telegram_id: int, resume_text: str, job_id: str) -> bool:
    """
    Send customized resume to user
    
    Args:
        telegram_id: User's Telegram ID
        resume_text: Customized resume text
        job_id: Job ID
        
    Returns:
        Success boolean
    """
    try:
        # Send introduction message
        intro_message = (
            "✅ *Your Customized Resume is Ready!*\n\n"
            "I've tailored your resume for the job you selected. Review it carefully before applying, "
            "and make any final adjustments to match your preferences."
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Save Resume", callback_data=f"save_resume_{job_id}")],
            [InlineKeyboardButton("Apply for Job", callback_data=f"apply_job_{job_id}")]
        ])
        
        # Send introduction
        await send_telegram_message(
            telegram_id=telegram_id,
            text=intro_message,
            reply_markup=keyboard
        )
        
        # Send the resume as a separate message
        # We may need to chunk it if it's too long for Telegram
        max_length = 4000  # Telegram message max length
        
        if len(resume_text) <= max_length:
            await send_telegram_message(
                telegram_id=telegram_id,
                text=resume_text,
                parse_mode="Markdown"
            )
        else:
            # Split the resume into chunks
            chunks = [resume_text[i:i + max_length] for i in range(0, len(resume_text), max_length)]
            
            for i, chunk in enumerate(chunks):
                await send_telegram_message(
                    telegram_id=telegram_id,
                    text=f"*Part {i+1}/{len(chunks)}*\n\n{chunk}",
                    parse_mode="Markdown"
                )
                
                # Add a small delay between messages to avoid rate limiting
                await asyncio.sleep(0.5)
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending resume notification: {str(e)}")
        return False

async def send_subscription_expiry_reminder(telegram_id: int, days_left: int, subscription_id: int) -> bool:
    """
    Send reminder about subscription expiry
    
    Args:
        telegram_id: User's Telegram ID
        days_left: Number of days left before expiry
        subscription_id: Subscription ID
        
    Returns:
        Success boolean
    """
    try:
        # Get subscription details
        from services.user_service import get_user_subscription_details
        from models.user import User
        from utils.db import get_db
        from sqlalchemy.future import select
        
        async with get_db() as db:
            result = await db.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User not found with telegram_id {telegram_id}")
                return False
            
            has_subscription, subscription_details = await get_user_subscription_details(user.id)
            
            if not has_subscription or not subscription_details:
                logger.error(f"Subscription details not found for user {user.id}")
                return False
            
            # Create message based on days left
            if days_left > 5:
                # Early reminder
                message = (
                    f"📅 *Subscription Reminder*\n\n"
                    f"Your {subscription_details['plan_name']} subscription will expire in {days_left} days on "
                    f"{subscription_details['end_date']}.\n\n"
                    f"To ensure uninterrupted access to job updates, consider renewing your subscription."
                )
            elif days_left > 1:
                # Urgent reminder
                message = (
                    f"⚠️ *Subscription Expiring Soon*\n\n"
                    f"Your {subscription_details['plan_name']} subscription will expire in just {days_left} days on "
                    f"{subscription_details['end_date']}.\n\n"
                    f"Renew now to continue receiving job updates and resume customization services."
                )
            else:
                # Last day reminder
                message = (
                    f"🚨 *Subscription Expires Tomorrow*\n\n"
                    f"Your {subscription_details['plan_name']} subscription expires tomorrow on "
                    f"{subscription_details['end_date']}.\n\n"
                    f"This is your last chance to renew and maintain uninterrupted access to our services."
                )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Renew Subscription", callback_data=f"renew_{subscription_id}")],
                [InlineKeyboardButton("Subscription Plans", callback_data="subscription")]
            ])
            
            # Send notification
            return await send_telegram_message(
                telegram_id=telegram_id,
                text=message,
                reply_markup=keyboard
            )
    
    except Exception as e:
        logger.error(f"Error sending subscription expiry reminder: {str(e)}")
        return False

async def send_subscription_expired_notification(telegram_id: int, subscription_id: int) -> bool:
    """
    Send notification about expired subscription
    
    Args:
        telegram_id: User's Telegram ID
        subscription_id: Subscription ID
        
    Returns:
        Success boolean
    """
    try:
        message = (
            "⏰ *Subscription Expired*\n\n"
            "Your subscription has expired. You will no longer receive job updates or be able to use "
            "premium features like resume customization.\n\n"
            "Renew your subscription to continue receiving personalized job matches that fit your profile."
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Renew Subscription", callback_data=f"renew_{subscription_id}")],
            [InlineKeyboardButton("Subscription Plans", callback_data="subscription")]
        ])
        
        return await send_telegram_message(
            telegram_id=telegram_id,
            text=message,
            reply_markup=keyboard
        )
    
    except Exception as e:
        logger.error(f"Error sending subscription expired notification: {str(e)}")
        return False

async def broadcast_message_to_users(
    user_ids: List[int],
    message: str,
    parse_mode: str = "Markdown",
    reply_markup: Optional[InlineKeyboardMarkup] = None
) -> Dict[int, bool]:
    """
    Broadcast a message to multiple users
    
    Args:
        user_ids: List of user IDs
        message: Message text
        parse_mode: Parse mode (Markdown or HTML)
        reply_markup: Optional inline keyboard markup
        
    Returns:
        Dictionary mapping user IDs to success status
    """
    results = {}
    
    for user_id in user_ids:
        try:
            # Get user's telegram ID
            from models.user import User
            from utils.db import get_db
            from sqlalchemy.future import select
            
            async with get_db() as db:
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"User not found: {user_id}")
                    results[user_id] = False
                    continue
                
                # Send message
                success = await send_telegram_message(
                    telegram_id=user.telegram_id,
                    text=message,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
                
                results[user_id] = success
                
                # Add a small delay to avoid rate limiting
                await asyncio.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Error broadcasting message to user {user_id}: {str(e)}")
            results[user_id] = False
    
    return results