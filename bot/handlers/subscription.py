# # bot/handlers/subscription.py
# import logging
# from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.ext import ContextTypes

# logger = logging.getLogger(__name__)

# async def subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle the subscription button callback"""
#     query = update.callback_query
#     await query.answer()
    
#     # Display subscription plans
#     plans_text = (
#         "📱 *Subscription Plans*\n\n"
#         "*Basic Plan - ₹199/week*\n"
#         "• 7-day subscription\n"
#         "• 2 daily job updates\n"
#         "• Basic resume assistance\n\n"
        
#         "*Premium Plan - ₹499/month*\n"
#         "• 30-day subscription\n"
#         "• Priority job updates\n"
#         "• Advanced resume customization\n\n"
        
#         "*Professional Plan - ₹999/3 months*\n"
#         "• 90-day subscription\n"
#         "• Premium job updates\n"
#         "• Unlimited resume customization\n"
#         "• Interview preparation\n\n"
        
#         "Select a plan below to subscribe:"
#     )
    
#     keyboard = InlineKeyboardMarkup([
#         [InlineKeyboardButton("Basic - ₹199/week", callback_data="plan_basic")],
#         [InlineKeyboardButton("Premium - ₹499/month", callback_data="plan_premium")],
#         [InlineKeyboardButton("Professional - ₹999/3 months", callback_data="plan_professional")],
#         [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
#     ])
    
#     await query.edit_message_text(
#         text=plans_text,
#         reply_markup=keyboard,
#         parse_mode="Markdown"
#     )

# async def plan_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle plan selection callback"""
#     query = update.callback_query
#     await query.answer()
    
#     # Extract plan type from callback data
#     plan_type = query.data.split("_")[1]
    
#     # Store selected plan in context
#     context.user_data["selected_plan"] = plan_type
    
#     # Ask for email
#     email_text = (
#         "Please enter your email address to receive payment confirmation and subscription details.\n\n"
#         "We'll also use this email to notify you about new job matches and subscription renewals."
#     )
    
#     # Set waiting for email flag
#     context.user_data["waiting_for_email"] = True
    
#     keyboard = InlineKeyboardMarkup([
#         [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
#     ])
    
#     await query.edit_message_text(email_text, reply_markup=keyboard)

# async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle back to main menu button"""
#     query = update.callback_query
#     await query.answer()
    
#     # Import here to avoid circular import
#     from bot.handlers.start import start_callback
    
#     # Call the start callback to show main menu
#     await start_callback(update, context)

# async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle about button callback"""
#     query = update.callback_query
#     await query.answer()
    
#     about_text = (
#         "📋 *About Job Updates Bot*\n\n"
#         "This bot helps you find job opportunities tailored to your resume and career goals.\n\n"
        
#         "*How it works:*\n"
#         "1. Subscribe to a plan\n"
#         "2. Upload your resume\n"
#         "3. Receive personalized job matches\n"
#         "4. Get customized resumes for specific jobs\n\n"
        
#         "We use AI to analyze your resume and match it with job listings from across the internet. "
#         "Our algorithms consider your skills, experience, and preferences to find the best opportunities for you.\n\n"
        
#         "For any questions or assistance, use the Support option in the main menu."
#     )
    
#     keyboard = InlineKeyboardMarkup([
#         [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
#     ])
    
#     await query.edit_message_text(
#         text=about_text,
#         reply_markup=keyboard,
#         parse_mode="Markdown"
#     )

# Important: Update this line to import plan_selected_callback from payment.py instead of defining it here

# bot/handlers/subscription.py
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the subscription button callback"""
    query = update.callback_query
    await query.answer()
    
    # Display subscription plans
    plans_text = (
        "📱 *Subscription Plans*\n\n"
        "*Basic Plan - ₹199/week*\n"
        "• 7-day subscription\n"
        "• 2 daily job updates\n"
        "• Basic resume assistance\n\n"
        
        "*Premium Plan - ₹499/month*\n"
        "• 30-day subscription\n"
        "• Priority job updates\n"
        "• Advanced resume customization\n\n"
        
        "*Professional Plan - ₹999/3 months*\n"
        "• 90-day subscription\n"
        "• Premium job updates\n"
        "• Unlimited resume customization\n"
        "• Interview preparation\n\n"
        
        "Select a plan below to subscribe:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Basic - ₹199/week", callback_data="plan_basic")],
        [InlineKeyboardButton("Premium - ₹499/month", callback_data="plan_premium")],
        [InlineKeyboardButton("Professional - ₹999/3 months", callback_data="plan_professional")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])
    
    await query.edit_message_text(
        text=plans_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Import this from payment.py instead of defining here
from bot.handlers.payment import plan_selected_callback

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to main menu button"""
    query = update.callback_query
    await query.answer()
    
    # Import here to avoid circular import
    from bot.handlers.start import start_callback
    
    # Call the start callback to show main menu
    await start_callback(update, context)

async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle about button callback"""
    query = update.callback_query
    await query.answer()
    
    about_text = (
        "📋 *About Job Updates Bot*\n\n"
        "This bot helps you find job opportunities tailored to your resume and career goals.\n\n"
        
        "*How it works:*\n"
        "1. Subscribe to a plan\n"
        "2. Upload your resume\n"
        "3. Receive personalized job matches\n"
        "4. Get customized resumes for specific jobs\n\n"
        
        "We use AI to analyze your resume and match it with job listings from across the internet. "
        "Our algorithms consider your skills, experience, and preferences to find the best opportunities for you.\n\n"
        
        "For any questions or assistance, use the Support option in the main menu."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])
    
    await query.edit_message_text(
        text=about_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )