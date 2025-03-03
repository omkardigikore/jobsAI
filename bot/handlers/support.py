# bot/handlers/support.py
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support button callback"""
    query = update.callback_query
    await query.answer()
    
    # Set support mode flag in user data
    context.user_data["support_mode"] = True
    
    support_text = (
        "🤝 *Support*\n\n"
        "You're now in support mode. Please describe your issue or question, "
        "and our AI assistant will help you.\n\n"
        "Type your message below, or click 'Exit Support' to return to the main menu."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Exit Support", callback_data="exit_support")]
    ])
    
    await query.edit_message_text(
        text=support_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def support_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages in support mode"""
    await update.message.reply_text(
        "Thank you for your message. Our support team will get back to you soon.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Exit Support", callback_data="exit_support")]
        ])
    )

async def exit_support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle exit support button callback"""
    query = update.callback_query
    await query.answer()
    
    # Clear support mode flag
    context.user_data.pop("support_mode", None)
    
    # Show main menu
    from bot.keyboards import get_main_menu_keyboard
    
    # We'll create a simple version without requiring database access for now
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")],
        [InlineKeyboardButton("📋 About", callback_data="about")],
        [InlineKeyboardButton("🤝 Support", callback_data="support")]
    ])
    
    await query.edit_message_text(
        text="You've exited support mode. How else can I help you today?",
        reply_markup=keyboard
    )

async def escalate_support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle escalation to human support agent"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=(
            "Your request has been escalated to our human support team. "
            "Someone will contact you shortly. Thank you for your patience."
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Exit Support", callback_data="exit_support")]
        ])
    )