# bot/handlers/start.py
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command to initiate bot interaction"""
    user = update.effective_user
    
    # Simple version without database access for now
    welcome_text = (
        f"👋 Hello, {user.first_name}!\n\n"
        f"Welcome to the Job Updates Bot. I can help you find the perfect job opportunities "
        f"tailored to your resume and career goals.\n\n"
        f"Our services include:\n"
        f"• Daily personalized job updates\n"
        f"• AI-powered resume customization\n"
        f"• Job application support\n\n"
        f"Choose an option below to get started!"
    )
    
    # Get main menu keyboard - simplified version without DB lookup
    keyboard = get_main_menu_keyboard()
    
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callbacks that return to main menu"""
    query = update.callback_query
    
    user = update.effective_user
    
    welcome_text = (
        f"👋 Hello, {user.first_name}!\n\n"
        f"Welcome to the Job Updates Bot. I can help you find the perfect job opportunities "
        f"tailored to your resume and career goals.\n\n"
        f"Our services include:\n"
        f"• Daily personalized job updates\n"
        f"• AI-powered resume customization\n"
        f"• Job application support\n\n"
        f"Choose an option below to get started!"
    )
    
    # Get main menu keyboard - simplified version without DB lookup
    keyboard = get_main_menu_keyboard()
    
    await query.edit_message_text(welcome_text, reply_markup=keyboard)