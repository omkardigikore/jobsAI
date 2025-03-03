# bot/keyboards.py
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard(user=None):
    """Generate the main menu keyboard based on user status"""
    keyboard = [
        [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")],
        [InlineKeyboardButton("📋 About", callback_data="about")],
        [InlineKeyboardButton("🤝 Support", callback_data="support")]
    ]
    
    # Add resume upload button if user has an active subscription but no resume
    if user and user.has_active_subscription and not user.has_resume:
        keyboard.insert(1, [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")])
    
    # Add "My Jobs" button if user has active subscription and resume
    if user and user.has_active_subscription and user.has_resume:
        keyboard.insert(1, [InlineKeyboardButton("🔍 My Job Updates", callback_data="my_jobs")])
    
    return InlineKeyboardMarkup(keyboard)

def get_subscription_plans_keyboard():
    """Generate keyboard with subscription plans"""
    keyboard = [
        [InlineKeyboardButton("Basic - ₹199/week", callback_data="plan_basic")],
        [InlineKeyboardButton("Premium - ₹499/month", callback_data="plan_premium")],
        [InlineKeyboardButton("Professional - ₹999/3months", callback_data="plan_professional")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)