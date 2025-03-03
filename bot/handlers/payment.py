# # bot/handlers/payment.py
# import logging
# import re
# from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.ext import ContextTypes

# logger = logging.getLogger(__name__)

# # Subscription plan details
# SUBSCRIPTION_PLANS = {
#     "basic": {
#         "name": "Basic",
#         "price": 199,  # in rupees
#         "duration_days": 7,
#         "features": ["2 daily job updates", "Basic resume assistance"]
#     },
#     "premium": {
#         "name": "Premium",
#         "price": 499,  # in rupees
#         "duration_days": 30,
#         "features": ["Priority job updates", "Advanced resume customization"]
#     },
#     "professional": {
#         "name": "Professional",
#         "price": 999,  # in rupees
#         "duration_days": 90,
#         "features": ["Premium job updates", "Unlimited resume customization", "Interview preparation"]
#     }
# }

# async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Process the email input for payment"""
#     email = update.message.text.strip()
    
#     # Validate email format
#     if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
#         await update.message.reply_text(
#             "Please enter a valid email address. Try again:"
#         )
#         return
    
#     # Get user ID and selected plan
#     selected_plan = context.user_data.get("selected_plan")
    
#     if not selected_plan:
#         await update.message.reply_text(
#             "There was an error processing your request. Please start over with /start command."
#         )
#         return
    
#     # Clear waiting flag
#     context.user_data["waiting_for_email"] = False
    
#     # Store email in context
#     context.user_data["email"] = email
    
#     # In a real implementation, we would generate a payment link here
#     # For now, simulate the payment process
#     try:
#         # Get plan details
#         plan_details = SUBSCRIPTION_PLANS.get(selected_plan)
        
#         if not plan_details:
#             raise ValueError(f"Invalid plan: {selected_plan}")
        
#         # Generate a dummy payment link
#         payment_link = f"https://razorpay.com/payment/demo?amount={plan_details['price']}00&email={email}"
        
#         # Send payment message
#         payment_text = (
#             f"Thanks for providing your email. In a real implementation, you would now proceed to payment.\n\n"
#             f"*Selected Plan:* {plan_details['name']}\n"
#             f"*Price:* ₹{plan_details['price']}\n"
#             f"*Duration:* {plan_details['duration_days']} days\n\n"
#             f"For this demo version, let's assume payment was successful."
#         )
        
#         # Send message with payment details
#         await update.message.reply_text(
#             payment_text,
#             parse_mode="Markdown"
#         )
        
#         # Simulate payment success
#         await simulate_payment_success(update, context, selected_plan)
        
#     except Exception as e:
#         logger.error(f"Error in payment process: {str(e)}")
#         await update.message.reply_text(
#             "Sorry, something went wrong processing your request. Please try again later.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
#             ])
#         )

# async def simulate_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE, plan_type: str):
#     """Simulate payment success and subscription activation"""
#     try:
#         plan_details = SUBSCRIPTION_PLANS.get(plan_type)
        
#         # Send success message
#         success_text = (
#             "🎉 *Payment Successful!*\n\n"
#             f"Thank you for subscribing to our {plan_details['name']} plan.\n"
#             f"Your subscription is now active for {plan_details['duration_days']} days.\n\n"
#             "Next step: Please upload your resume to start receiving personalized job updates."
#         )
        
#         keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
#             [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#         ])
        
#         await update.message.reply_text(
#             success_text,
#             reply_markup=keyboard,
#             parse_mode="Markdown"
#         )
        
#         # Set user as subscribed in context
#         context.user_data["is_subscribed"] = True
#         context.user_data["subscription_plan"] = plan_type
        
#     except Exception as e:
#         logger.error(f"Error simulating payment success: {str(e)}")
#         await update.message.reply_text(
#             "Sorry, something went wrong processing your subscription. Please contact support.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🤝 Support", callback_data="support")],
#                 [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#             ])
#         )

# async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle payment verification callback"""
#     query = update.callback_query
#     await query.answer()
    
#     # Extract order ID from callback data
#     callback_parts = query.data.split("_")
#     if len(callback_parts) < 3 or callback_parts[1] != "check":
#         await query.edit_message_text("Invalid payment request. Please start over with /start command.")
#         return
    
#     # In a real implementation, verify payment status with Razorpay
#     # For now, simulate successful payment
    
#     # Get selected plan
#     selected_plan = context.user_data.get("selected_plan")
#     if not selected_plan:
#         await query.edit_message_text(
#             "There was an error processing your request. Please start over with /start command."
#         )
#         return
    
#     # Simulate payment success
#     plan_details = SUBSCRIPTION_PLANS.get(selected_plan)
    
#     # Send success message
#     success_text = (
#         "🎉 *Payment Successful!*\n\n"
#         f"Thank you for subscribing to our {plan_details['name']} plan.\n"
#         f"Your subscription is now active for {plan_details['duration_days']} days.\n\n"
#         "Next step: Please upload your resume to start receiving personalized job updates."
#     )
    
#     keyboard = InlineKeyboardMarkup([
#         [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
#         [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#     ])
    
#     await query.edit_message_text(
#         success_text,
#         reply_markup=keyboard,
#         parse_mode="Markdown"
#     )
    
#     # Set user as subscribed in context
#     context.user_data["is_subscribed"] = True
#     context.user_data["subscription_plan"] = selected_plan

#store is not stored below only cache data 

# # bot/handlers/payment.py
# import logging
# import re
# import json
# import razorpay
# from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.ext import ContextTypes
# from config.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, WEBHOOK_URL

# logger = logging.getLogger(__name__)

# # Initialize Razorpay client
# client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# # Subscription plan details
# SUBSCRIPTION_PLANS = {
#     "basic": {
#         "name": "Basic",
#         "price": 199,  # in rupees
#         "duration_days": 7,
#         "features": ["2 daily job updates", "Basic resume assistance"]
#     },
#     "premium": {
#         "name": "Premium",
#         "price": 499,  # in rupees
#         "duration_days": 30,
#         "features": ["Priority job updates", "Advanced resume customization"]
#     },
#     "professional": {
#         "name": "Professional",
#         "price": 999,  # in rupees
#         "duration_days": 90,
#         "features": ["Premium job updates", "Unlimited resume customization", "Interview preparation"]
#     }
# }

# # User info collection steps
# USER_INFO_STEPS = [
#     {
#         "field": "email",
#         "prompt": "Please enter your email address:",
#         "validation": lambda x: re.match(r"[^@]+@[^@]+\.[^@]+", x),
#         "error_message": "Please enter a valid email address."
#     },
#     {
#         "field": "first_name",
#         "prompt": "Please enter your first name:",
#         "validation": lambda x: len(x) >= 2,
#         "error_message": "First name should be at least 2 characters."
#     },
#     {
#         "field": "last_name",
#         "prompt": "Please enter your last name:",
#         "validation": lambda x: len(x) >= 2,
#         "error_message": "Last name should be at least 2 characters."
#     },
#     {
#         "field": "mobile",
#         "prompt": "Please enter your mobile number (10 digits):",
#         "validation": lambda x: re.match(r"^\d{10}$", x),
#         "error_message": "Please enter a valid 10-digit mobile number."
#     },
#     {
#         "field": "state",
#         "prompt": "Please enter your state:",
#         "validation": lambda x: len(x) >= 2,
#         "error_message": "State name should be at least 2 characters."
#     },
#     {
#         "field": "city",
#         "prompt": "Please enter your city:",
#         "validation": lambda x: len(x) >= 2,
#         "error_message": "City name should be at least 2 characters."
#     },
#     {
#         "field": "job_profile",
#         "prompt": "What job profile are you looking for?",
#         "validation": lambda x: len(x) >= 3,
#         "error_message": "Please enter a valid job profile (at least 3 characters)."
#     }
# ]

# async def plan_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle plan selection callback"""
#     query = update.callback_query
#     await query.answer()
    
#     # Extract plan type from callback data
#     plan_type = query.data.split("_")[1]
    
#     # Store selected plan in context
#     context.user_data["selected_plan"] = plan_type
    
#     # Start user info collection process
#     await start_user_info_collection(update, context)

# async def start_user_info_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Start the user information collection process"""
#     # Initialize user_info dict if it doesn't exist
#     if "user_info" not in context.user_data:
#         context.user_data["user_info"] = {}
    
#     # Initialize current_step if it doesn't exist
#     if "current_info_step" not in context.user_data:
#         context.user_data["current_info_step"] = 0
    
#     # Get current step
#     current_step = context.user_data["current_info_step"]
    
#     # Check if we've finished collecting info
#     if current_step >= len(USER_INFO_STEPS):
#         # Process payment
#         await generate_payment_link(update, context)
#         return
    
#     # Get step info
#     step_info = USER_INFO_STEPS[current_step]
    
#     # Send prompt for current step
#     if hasattr(update, 'callback_query'):
#         # If this is from a callback query
#         await update.callback_query.edit_message_text(
#             text=step_info["prompt"],
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
#             ])
#         )
#     else:
#         # If this is from a message
#         await update.message.reply_text(
#             text=step_info["prompt"],
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
#             ])
#         )
    
#     # Set waiting flag
#     context.user_data["waiting_for_info"] = True

# async def process_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Process user information input"""
#     if not context.user_data.get("waiting_for_info", False):
#         return False
    
#     # Get current step
#     current_step = context.user_data.get("current_info_step", 0)
    
#     if current_step >= len(USER_INFO_STEPS):
#         # We've collected all info, this shouldn't happen
#         context.user_data["waiting_for_info"] = False
#         return False
    
#     # Get step info
#     step_info = USER_INFO_STEPS[current_step]
    
#     # Get user input
#     user_input = update.message.text.strip()
    
#     # Validate input
#     if not step_info["validation"](user_input):
#         await update.message.reply_text(
#             text=step_info["error_message"] + " Please try again.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
#             ])
#         )
#         return True
    
#     # Store valid input
#     context.user_data["user_info"][step_info["field"]] = user_input
    
#     # Move to next step
#     context.user_data["current_info_step"] += 1
#     current_step = context.user_data["current_info_step"]
    
#     # Check if we've collected all info
#     if current_step >= len(USER_INFO_STEPS):
#         # Show summary and confirm
#         await show_info_summary(update, context)
#     else:
#         # Request next piece of info
#         next_step = USER_INFO_STEPS[current_step]
#         await update.message.reply_text(next_step["prompt"])
    
#     return True

# async def show_info_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Show summary of collected info and ask for confirmation"""
#     user_info = context.user_data["user_info"]
#     plan_type = context.user_data["selected_plan"]
#     plan_details = SUBSCRIPTION_PLANS[plan_type]
    
#     # Create summary message
#     summary = (
#         "📋 *Information Summary*\n\n"
#         f"*Selected Plan:* {plan_details['name']}\n"
#         f"*Price:* ₹{plan_details['price']}\n"
#         f"*Duration:* {plan_details['duration_days']} days\n\n"
        
#         "*Your Information:*\n"
#         f"*Name:* {user_info['first_name']} {user_info['last_name']}\n"
#         f"*Email:* {user_info['email']}\n"
#         f"*Mobile:* {user_info['mobile']}\n"
#         f"*Location:* {user_info['city']}, {user_info['state']}\n"
#         f"*Job Profile:* {user_info['job_profile']}\n\n"
        
#         "Please confirm if the information is correct to proceed with payment."
#     )
    
#     # Add confirmation buttons
#     keyboard = InlineKeyboardMarkup([
#         [InlineKeyboardButton("✅ Confirm & Pay", callback_data="confirm_payment")],
#         [InlineKeyboardButton("🔄 Edit Information", callback_data="edit_info")],
#         [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
#     ])
    
#     # Send summary
#     await update.message.reply_text(
#         text=summary,
#         reply_markup=keyboard,
#         parse_mode="Markdown"
#     )
    
#     # Clear waiting flag
#     context.user_data["waiting_for_info"] = False

# async def confirm_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle payment confirmation callback"""
#     query = update.callback_query
#     await query.answer()
    
#     # Generate payment link
#     await generate_payment_link(update, context)

# async def edit_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle edit information callback"""
#     query = update.callback_query
#     await query.answer()
    
#     # Reset information collection process
#     context.user_data["current_info_step"] = 0
#     context.user_data["user_info"] = {}
    
#     # Start collection again
#     await start_user_info_collection(update, context)

# async def generate_payment_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Generate Razorpay payment link"""
#     user_info = context.user_data.get("user_info", {})
#     plan_type = context.user_data.get("selected_plan")
    
#     if not plan_type or not user_info:
#         # Handle missing info
#         if hasattr(update, 'callback_query'):
#             await update.callback_query.edit_message_text(
#                 "There was an error processing your request. Please try again."
#             )
#         else:
#             await update.message.reply_text(
#                 "There was an error processing your request. Please try again."
#             )
#         return
    
#     try:
#         # Get plan details
#         plan_details = SUBSCRIPTION_PLANS[plan_type]
        
#         # Create unique receipt ID
#         import uuid
#         import time
#         receipt_id = f"rcpt_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
#         # Create Razorpay order
#         order_amount = plan_details["price"] * 100  # Convert to paise
#         order_currency = "INR"
        
#         order_data = {
#             "amount": order_amount,
#             "currency": order_currency,
#             "receipt": receipt_id,
#             "notes": {
#                 "plan_type": plan_type,
#                 "telegram_id": str(update.effective_user.id),
#                 "first_name": user_info.get("first_name", ""),
#                 "last_name": user_info.get("last_name", ""),
#                 "email": user_info.get("email", ""),
#                 "mobile": user_info.get("mobile", ""),
#                 "state": user_info.get("state", ""),
#                 "city": user_info.get("city", ""),
#                 "job_profile": user_info.get("job_profile", "")
#             }
#         }
        
#         # Create order
#         order = client.order.create(data=order_data)
#         order_id = order["id"]
        
#         # Store order ID in context
#         context.user_data["razorpay_order_id"] = order_id
        
#         payment_link_data = {
#         "amount": order_amount,
#         "currency": order_currency,
#         "accept_partial": False,
#         "description": f"{plan_details['name']} Subscription - Job Updates Bot",
#         "customer": {
#             "name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}",
#             "email": user_info.get("email", ""),
#             "contact": user_info.get("mobile", "")
#         },
#         "notify": {
#             "email": True,
#             "sms": True
#         },
#         "reminder_enable": True,
#         "notes": order_data["notes"],
#         # Remove any path from WEBHOOK_URL in case it's already included
#         # "callback_url": f"{WEBHOOK_URL.rstrip('/')}?order_id={order_id}",
#         "callback_url": f"{WEBHOOK_URL}api/v1/payments/webhook/razorpay?order_id={order_id}",
#         "callback_method": "get"
#     }
        
#         # Create payment link
#         try:
#             payment_link = client.payment_link.create(payment_link_data)
#             payment_link_url = payment_link["short_url"]
            
#             # Store payment link info
#             context.user_data["payment_link"] = payment_link
            
#             # Send payment link
#             payment_text = (
#                 "🔐 *Payment Link Generated*\n\n"
#                 f"Plan: *{plan_details['name']}*\n"
#                 f"Amount: *₹{plan_details['price']}*\n\n"
#                 "Click the button below to make the payment. Once payment is complete, you'll be automatically subscribed."
#             )
            
#             keyboard = InlineKeyboardMarkup([
#                 [InlineKeyboardButton("💳 Pay Now", url=payment_link_url)],
#                 [InlineKeyboardButton("I've Completed Payment", callback_data=f"payment_check_{order_id}")],
#                 [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
#             ])
            
#             if hasattr(update, 'callback_query'):
#                 await update.callback_query.edit_message_text(
#                     text=payment_text,
#                     reply_markup=keyboard,
#                     parse_mode="Markdown"
#                 )
#             else:
#                 await update.message.reply_text(
#                     text=payment_text,
#                     reply_markup=keyboard,
#                     parse_mode="Markdown"
#                 )
            
#         except Exception as e:
#             logger.error(f"Error creating Razorpay payment link: {str(e)}")
#             payment_text = "There was an error generating your payment link. Please try again later."
            
#             if hasattr(update, 'callback_query'):
#                 await update.callback_query.edit_message_text(text=payment_text)
#             else:
#                 await update.message.reply_text(text=payment_text)
    
#     except Exception as e:
#         logger.error(f"Error generating payment: {str(e)}")
#         error_text = "Sorry, something went wrong with the payment process. Please try again later."
        
#         if hasattr(update, 'callback_query'):
#             await update.callback_query.edit_message_text(text=error_text)
#         else:
#             await update.message.reply_text(text=error_text)

# async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle payment verification callback"""
#     query = update.callback_query
#     await query.answer()
    
#     # Extract order ID from callback data
#     callback_parts = query.data.split("_")
#     if len(callback_parts) < 3 or callback_parts[1] != "check":
#         await query.edit_message_text("Invalid payment request. Please start over with /start command.")
#         return
    
#     order_id = callback_parts[2]
    
#     # Verify payment status with Razorpay
#     try:
#         # Fetch order from Razorpay
#         order = client.order.fetch(order_id)
        
#         # Check if payment is successful
#         if order["status"] == "paid":
#             # Payment successful
#             # Get selected plan
#             plan_type = context.user_data.get("selected_plan")
#             plan_details = SUBSCRIPTION_PLANS.get(plan_type)
            
#             # Set user as subscribed in context
#             context.user_data["is_subscribed"] = True
#             context.user_data["subscription_plan"] = plan_type
            
#             # Send success message
#             success_text = (
#                 "🎉 *Payment Successful!*\n\n"
#                 f"Thank you for subscribing to our {plan_details['name']} plan.\n"
#                 f"Your subscription is now active for {plan_details['duration_days']} days.\n\n"
#                 "Next step: Please upload your resume to start receiving personalized job updates."
#             )
            
#             keyboard = InlineKeyboardMarkup([
#                 [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
#                 [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#             ])
            
#             await query.edit_message_text(
#                 success_text,
#                 reply_markup=keyboard,
#                 parse_mode="Markdown"
#             )
#         else:
#             # Payment not yet completed
#             await query.edit_message_text(
#                 "Your payment is not yet complete. Please complete the payment process.\n\n"
#                 "If you've already paid, it may take a few moments to reflect in our system. "
#                 "You can check again in a minute.",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Check Again", callback_data=f"payment_check_{order_id}")],
#                     [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
#                 ])
#             )
    
#     except Exception as e:
#         logger.error(f"Error verifying payment: {str(e)}")
#         await query.edit_message_text(
#             "There was an error verifying your payment. If you've completed the payment, "
#             "please contact support for assistance.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🤝 Support", callback_data="support")],
#                 [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#             ])
#         )

# async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Legacy function to maintain compatibility - replaced by process_user_info"""
#     # This function is kept for backward compatibility
#     # The functionality is now handled by the step-by-step user_info collection
#     return await process_user_info(update, context)

#data is stored in user_data 
# bot/handlers/payment.py
# import logging
# import re
# from datetime import datetime, timedelta
# from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.ext import ContextTypes

# from utils.db import get_db
# from models.user import User
# from models.subscription import Subscription, SubscriptionPlan
# from models.payment import Payment
# from sqlalchemy.future import select

# logger = logging.getLogger(__name__)

# # Subscription plan details
# SUBSCRIPTION_PLANS = {
#     "basic": {
#         "name": "Basic",
#         "price": 199,  # in rupees
#         "duration_days": 7,
#         "features": ["2 daily job updates", "Basic resume assistance"]
#     },
#     "premium": {
#         "name": "Premium",
#         "price": 499,  # in rupees
#         "duration_days": 30,
#         "features": ["Priority job updates", "Advanced resume customization"]
#     },
#     "professional": {
#         "name": "Professional",
#         "price": 999,  # in rupees
#         "duration_days": 90,
#         "features": ["Premium job updates", "Unlimited resume customization", "Interview preparation"]
#     }
# }

# async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Process the email input for payment"""
#     email = update.message.text.strip()
    
#     # Validate email format
#     if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
#         await update.message.reply_text(
#             "Please enter a valid email address. Try again:"
#         )
#         return
    
#     # Get user ID and selected plan
#     selected_plan = context.user_data.get("selected_plan")
    
#     if not selected_plan:
#         await update.message.reply_text(
#             "There was an error processing your request. Please start over with /start command."
#         )
#         return
    
#     # Clear waiting flag
#     context.user_data["waiting_for_email"] = False
    
#     # Store email in context
#     context.user_data["email"] = email
    
#     telegram_id = update.effective_user.id
    
#     # Update user's email in the database
#     try:
#         async with get_db() as db:
#             # Find or create user
#             result = await db.execute(select(User).where(User.telegram_id == telegram_id))
#             user = result.scalar_one_or_none()
            
#             if not user:
#                 # Create new user
#                 user = User(
#                     telegram_id=telegram_id,
#                     username=update.effective_user.username,
#                     first_name=update.effective_user.first_name,
#                     last_name=update.effective_user.last_name,
#                     email=email
#                 )
#                 db.add(user)
#                 await db.flush()
#                 logger.info(f"Created new user with ID {user.id}")
#             else:
#                 # Update email
#                 user.email = email
#                 logger.info(f"Updated email for user ID {user.id}")
            
#             # Store user ID in context for later use
#             context.user_data["db_user_id"] = user.id
            
#             await db.commit()
#     except Exception as e:
#         logger.error(f"Error updating user email: {str(e)}")
#         await update.message.reply_text(
#             "Sorry, something went wrong processing your request. Please try again later."
#         )
#         return
    
#     # In a real implementation, we would generate a payment link here
#     # For now, simulate the payment process
#     try:
#         # Get plan details
#         plan_details = SUBSCRIPTION_PLANS.get(selected_plan)
        
#         if not plan_details:
#             raise ValueError(f"Invalid plan: {selected_plan}")
        
#         # Generate a dummy payment link
#         payment_link = f"https://razorpay.com/payment/demo?amount={plan_details['price']}00&email={email}"
        
#         # Send payment message
#         payment_text = (
#             f"Thanks for providing your email. In a real implementation, you would now proceed to payment.\n\n"
#             f"*Selected Plan:* {plan_details['name']}\n"
#             f"*Price:* ₹{plan_details['price']}\n"
#             f"*Duration:* {plan_details['duration_days']} days\n\n"
#             f"For this demo version, let's assume payment was successful."
#         )
        
#         # Send message with payment details
#         await update.message.reply_text(
#             payment_text,
#             parse_mode="Markdown"
#         )
        
#         # Simulate payment success
#         await create_subscription_in_db(context.user_data["db_user_id"], selected_plan)
        
#         # Simulate payment success message
#         await simulate_payment_success(update, context, selected_plan)
        
#     except Exception as e:
#         logger.error(f"Error in payment process: {str(e)}")
#         await update.message.reply_text(
#             "Sorry, something went wrong processing your request. Please try again later.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
#             ])
#         )

# async def create_subscription_in_db(user_id: int, plan_type: str):
#     """Create a subscription record in the database"""
#     try:
#         plan_details = SUBSCRIPTION_PLANS.get(plan_type)
#         if not plan_details:
#             raise ValueError(f"Invalid plan type: {plan_type}")
        
#         async with get_db() as db:
#             # Get plan from database
#             result = await db.execute(
#                 select(SubscriptionPlan).where(SubscriptionPlan.name == plan_details["name"])
#             )
            
#             plan = result.scalar_one_or_none()
            
#             if not plan:
#                 raise ValueError(f"Plan not found in database: {plan_details['name']}")
            
#             # Create subscription
#             start_date = datetime.utcnow()
#             end_date = start_date + timedelta(days=plan_details["duration_days"])
            
#             subscription = Subscription(
#                 user_id=user_id,
#                 plan_id=plan.id,
#                 start_date=start_date,
#                 end_date=end_date,
#                 is_active=True,
#                 is_trial=False,
#                 subscription_metadata={"source": "telegram_bot"}
#             )
            
#             db.add(subscription)
#             await db.flush()
            
#             # Create payment record
#             payment = Payment(
#                 user_id=user_id,
#                 subscription_id=subscription.id,
#                 amount=plan.price,
#                 currency="INR",
#                 payment_id=f"demo_payment_{datetime.utcnow().timestamp()}",
#                 order_id=f"demo_order_{datetime.utcnow().timestamp()}",
#                 status="captured",
#                 payment_method="simulated"
#             )
            
#             db.add(payment)
#             await db.commit()
            
#             logger.info(f"Created subscription {subscription.id} for user {user_id}")
#             return subscription.id
            
#     except Exception as e:
#         logger.error(f"Error creating subscription in database: {str(e)}")
#         raise

# async def simulate_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE, plan_type: str):
#     """Simulate payment success and subscription activation"""
#     try:
#         plan_details = SUBSCRIPTION_PLANS.get(plan_type)
        
#         # Send success message
#         success_text = (
#             "🎉 *Payment Successful!*\n\n"
#             f"Thank you for subscribing to our {plan_details['name']} plan.\n"
#             f"Your subscription is now active for {plan_details['duration_days']} days.\n\n"
#             "Next step: Please upload your resume to start receiving personalized job updates."
#         )
        
#         keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
#             [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#         ])
        
#         await update.message.reply_text(
#             success_text,
#             reply_markup=keyboard,
#             parse_mode="Markdown"
#         )
        
#     except Exception as e:
#         logger.error(f"Error simulating payment success: {str(e)}")
#         await update.message.reply_text(
#             "Sorry, something went wrong processing your subscription. Please contact support.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🤝 Support", callback_data="support")],
#                 [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#             ])
#         )

# async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle payment verification callback"""
#     query = update.callback_query
#     await query.answer()
    
#     # Extract order ID from callback data
#     callback_parts = query.data.split("_")
#     if len(callback_parts) < 3 or callback_parts[1] != "check":
#         await query.edit_message_text("Invalid payment request. Please start over with /start command.")
#         return
    
#     # In a real implementation, verify payment status with Razorpay
#     # For now, simulate successful payment
    
#     # Get selected plan
#     selected_plan = context.user_data.get("selected_plan")
#     if not selected_plan:
#         await query.edit_message_text(
#             "There was an error processing your request. Please start over with /start command."
#         )
#         return
    
#     # Simulate payment success
#     plan_details = SUBSCRIPTION_PLANS.get(selected_plan)
    
#     # Send success message
#     success_text = (
#         "🎉 *Payment Successful!*\n\n"
#         f"Thank you for subscribing to our {plan_details['name']} plan.\n"
#         f"Your subscription is now active for {plan_details['duration_days']} days.\n\n"
#         "Next step: Please upload your resume to start receiving personalized job updates."
#     )
    
#     keyboard = InlineKeyboardMarkup([
#         [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
#         [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#     ])
    
#     await query.edit_message_text(
#         success_text,
#         reply_markup=keyboard,
#         parse_mode="Markdown"
#     )



# bot/handlers/payment.py
import logging
import re
import json
import razorpay
import uuid
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, WEBHOOK_URL

from utils.db import get_db
from models.user import User
from models.subscription import Subscription, SubscriptionPlan
from models.payment import Payment
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Subscription plan details
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "price": 199,  # in rupees
        "duration_days": 7,
        "features": ["2 daily job updates", "Basic resume assistance"]
    },
    "premium": {
        "name": "Premium",
        "price": 499,  # in rupees
        "duration_days": 30,
        "features": ["Priority job updates", "Advanced resume customization"]
    },
    "professional": {
        "name": "Professional",
        "price": 999,  # in rupees
        "duration_days": 90,
        "features": ["Premium job updates", "Unlimited resume customization", "Interview preparation"]
    }
}

# User info collection steps
USER_INFO_STEPS = [
    {
        "field": "email",
        "prompt": "Please enter your email address:",
        "validation": lambda x: re.match(r"[^@]+@[^@]+\.[^@]+", x),
        "error_message": "Please enter a valid email address."
    },
    {
        "field": "first_name",
        "prompt": "Please enter your first name:",
        "validation": lambda x: len(x) >= 2,
        "error_message": "First name should be at least 2 characters."
    },
    {
        "field": "last_name",
        "prompt": "Please enter your last name:",
        "validation": lambda x: len(x) >= 2,
        "error_message": "Last name should be at least 2 characters."
    },
    {
        "field": "mobile",
        "prompt": "Please enter your mobile number (10 digits):",
        "validation": lambda x: re.match(r"^\d{10}$", x),
        "error_message": "Please enter a valid 10-digit mobile number."
    },
    {
        "field": "state",
        "prompt": "Please enter your state:",
        "validation": lambda x: len(x) >= 2,
        "error_message": "State name should be at least 2 characters."
    },
    {
        "field": "city",
        "prompt": "Please enter your city:",
        "validation": lambda x: len(x) >= 2,
        "error_message": "City name should be at least 2 characters."
    },
    {
        "field": "job_profile",
        "prompt": "What job profile are you looking for?",
        "validation": lambda x: len(x) >= 3,
        "error_message": "Please enter a valid job profile (at least 3 characters)."
    }
]

async def plan_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plan selection callback"""
    query = update.callback_query
    await query.answer()
    
    # Extract plan type from callback data
    plan_type = query.data.split("_")[1]
    
    # Store selected plan in context
    context.user_data["selected_plan"] = plan_type
    
    # Start user info collection process
    await start_user_info_collection(update, context)

async def start_user_info_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the user information collection process"""
    # Initialize user_info dict if it doesn't exist
    if "user_info" not in context.user_data:
        context.user_data["user_info"] = {}
    
    # Initialize current_step if it doesn't exist
    if "current_info_step" not in context.user_data:
        context.user_data["current_info_step"] = 0
    
    # Get current step
    current_step = context.user_data["current_info_step"]
    
    # Check if we've finished collecting info
    if current_step >= len(USER_INFO_STEPS):
        # Process payment
        await generate_payment_link(update, context)
        return
    
    # Get step info
    step_info = USER_INFO_STEPS[current_step]
    
    # Send prompt for current step
    if hasattr(update, 'callback_query'):
        # If this is from a callback query
        await update.callback_query.edit_message_text(
            text=step_info["prompt"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
            ])
        )
    else:
        # If this is from a message
        await update.message.reply_text(
            text=step_info["prompt"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
            ])
        )
    
    # Set waiting flag
    context.user_data["waiting_for_info"] = True

async def process_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process user information input"""

    print("process_user_info")
    if not context.user_data.get("waiting_for_info", False):
        return False
    
    # Get current step
    current_step = context.user_data.get("current_info_step", 0)
    
    if current_step >= len(USER_INFO_STEPS):
        # We've collected all info, this shouldn't happen
        context.user_data["waiting_for_info"] = False
        return False
    
    # Get step info
    step_info = USER_INFO_STEPS[current_step]
    
    # Get user input
    user_input = update.message.text.strip()
    
    # Validate input
    if not step_info["validation"](user_input):
        await update.message.reply_text(
            text=step_info["error_message"] + " Please try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
            ])
        )
        return True
    
    # Store valid input
    context.user_data["user_info"][step_info["field"]] = user_input
    
    # Move to next step
    context.user_data["current_info_step"] += 1
    current_step = context.user_data["current_info_step"]
    
    # Check if we've collected all info
    if current_step >= len(USER_INFO_STEPS):
        # Show summary and confirm
        await show_info_summary(update, context)
    else:
        # Request next piece of info
        next_step = USER_INFO_STEPS[current_step]
        await update.message.reply_text(next_step["prompt"])
    
    return True

async def show_info_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show summary of collected info and ask for confirmation"""
    user_info = context.user_data["user_info"]
    plan_type = context.user_data["selected_plan"]
    plan_details = SUBSCRIPTION_PLANS[plan_type]
    
    # Create summary message
    summary = (
        "📋 *Information Summary*\n\n"
        f"*Selected Plan:* {plan_details['name']}\n"
        f"*Price:* ₹{plan_details['price']}\n"
        f"*Duration:* {plan_details['duration_days']} days\n\n"
        
        "*Your Information:*\n"
        f"*Name:* {user_info['first_name']} {user_info['last_name']}\n"
        f"*Email:* {user_info['email']}\n"
        f"*Mobile:* {user_info['mobile']}\n"
        f"*Location:* {user_info['city']}, {user_info['state']}\n"
        f"*Job Profile:* {user_info['job_profile']}\n\n"
        
        "Please confirm if the information is correct to proceed with payment."
    )
    
    # Add confirmation buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm & Pay", callback_data="confirm_payment")],
        [InlineKeyboardButton("🔄 Edit Information", callback_data="edit_info")],
        [InlineKeyboardButton("🔙 Back to Plans", callback_data="subscription")]
    ])
    
    # Send summary
    await update.message.reply_text(
        text=summary,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    # Clear waiting flag
    context.user_data["waiting_for_info"] = False

async def confirm_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment confirmation callback"""
    query = update.callback_query
    await query.answer()
    
    # Save user info to database
    print("storing data in db")
    await save_user_to_database(update, context)
    
    # Generate payment link
    await generate_payment_link(update, context)

async def save_user_to_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save user information to the database"""
    user_info = context.user_data.get("user_info", {})
    telegram_id = update.effective_user.id
    
    try:
        async with get_db() as db:
            # Find or create user
            result = await db.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            
            if not user:
                # Create new user
                user = User(
                    telegram_id=telegram_id,
                    username=update.effective_user.username,
                    first_name=user_info.get("first_name", update.effective_user.first_name),
                    last_name=user_info.get("last_name", update.effective_user.last_name),
                    email=user_info.get("email", ""),
                    phone=user_info.get("mobile", ""),  # Changed to match User model field 'phone'
                    is_active=True,
                    has_resume=False
                )

                print("user info:",user)
                db.add(user)
                await db.flush()
                logger.info(f"Created new user with ID {user.id}")
            else:
                # Update user info
                user.first_name = user_info.get("first_name", user.first_name)
                user.last_name = user_info.get("last_name", user.last_name)
                user.email = user_info.get("email", user.email)
                user.phone = user_info.get("mobile", user.phone)  # Changed to match User model field 'phone'
                logger.info(f"Updated user info for user ID {user.id}")
            
            # Store user ID in context for later use
            context.user_data["db_user_id"] = user.id
            
            await db.commit()
            return user.id
    except Exception as e:
        logger.error(f"Error saving user to database: {str(e)}")
        return None

async def edit_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit information callback"""
    query = update.callback_query
    await query.answer()
    
    # Reset information collection process
    context.user_data["current_info_step"] = 0
    context.user_data["user_info"] = {}
    
    # Start collection again
    await start_user_info_collection(update, context)

async def generate_payment_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate Razorpay payment link"""
    user_info = context.user_data.get("user_info", {})
    plan_type = context.user_data.get("selected_plan")
    
    if not plan_type or not user_info:
        # Handle missing info
        if hasattr(update, 'callback_query'):
            await update.callback_query.edit_message_text(
                "There was an error processing your request. Please try again."
            )
        else:
            await update.message.reply_text(
                "There was an error processing your request. Please try again."
            )
        return
    
    try:
        # Get plan details
        plan_details = SUBSCRIPTION_PLANS[plan_type]
        
        # Create unique receipt ID
        receipt_id = f"rcpt_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        # Create Razorpay order
        order_amount = plan_details["price"] * 100  # Convert to paise
        order_currency = "INR"
        
        order_data = {
            "amount": order_amount,
            "currency": order_currency,
            "receipt": receipt_id,
            "notes": {
                "plan_type": plan_type,
                "telegram_id": str(update.effective_user.id),
                "first_name": user_info.get("first_name", ""),
                "last_name": user_info.get("last_name", ""),
                "email": user_info.get("email", ""),
                "mobile": user_info.get("mobile", ""),
                "state": user_info.get("state", ""),
                "city": user_info.get("city", ""),
                "job_profile": user_info.get("job_profile", "")
            }
        }
        
        # Create order
        order = client.order.create(data=order_data)
        order_id = order["id"]
        
        # Store order ID in context
        context.user_data["razorpay_order_id"] = order_id
        
        payment_link_data = {
            "amount": order_amount,
            "currency": order_currency,
            "accept_partial": False,
            "description": f"{plan_details['name']} Subscription - Job Updates Bot",
            "customer": {
                "name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}",
                "email": user_info.get("email", ""),
                "contact": user_info.get("mobile", "")
            },
            "notify": {
                "email": True,
                "sms": True
            },
            "reminder_enable": True,
            "notes": order_data["notes"],
            # Remove any path from WEBHOOK_URL in case it's already included
            "callback_url": f"{WEBHOOK_URL}api/v1/payments/webhook/razorpay?order_id={order_id}",
            "callback_method": "get"
        }
        
        # Create payment link
        try:
            payment_link = client.payment_link.create(payment_link_data)
            payment_link_url = payment_link["short_url"]
            
            # Store payment link info
            context.user_data["payment_link"] = payment_link
            
            # Create a pending payment record in database
            await create_pending_payment_in_db(
                context.user_data.get("db_user_id"),
                plan_type,
                order_id,
                payment_link.get("id", "")
            )
            
            # Send payment link
            payment_text = (
                "🔐 *Payment Link Generated*\n\n"
                f"Plan: *{plan_details['name']}*\n"
                f"Amount: *₹{plan_details['price']}*\n\n"
                "Click the button below to make the payment. Once payment is complete, you'll be automatically subscribed."
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Pay Now", url=payment_link_url)],
                [InlineKeyboardButton("I've Completed Payment", callback_data=f"payment_check_{order_id}")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
            ])
            
            if hasattr(update, 'callback_query'):
                await update.callback_query.edit_message_text(
                    text=payment_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text=payment_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            
        except Exception as e:
            logger.error(f"Error creating Razorpay payment link: {str(e)}")
            payment_text = "There was an error generating your payment link. Please try again later."
            
            if hasattr(update, 'callback_query'):
                await update.callback_query.edit_message_text(text=payment_text)
            else:
                await update.message.reply_text(text=payment_text)
    
    except Exception as e:
        logger.error(f"Error generating payment: {str(e)}")
        error_text = "Sorry, something went wrong with the payment process. Please try again later."
        
        if hasattr(update, 'callback_query'):
            await update.callback_query.edit_message_text(text=error_text)
        else:
            await update.message.reply_text(text=error_text)

async def create_pending_payment_in_db(user_id: int, plan_type: str, order_id: str, payment_link_id: str):
    """Create a pending payment record in the database"""
    try:
        if not user_id:
            logger.error("Cannot create payment record: user_id is None")
            return None
            
        plan_details = SUBSCRIPTION_PLANS.get(plan_type)
        if not plan_details:
            raise ValueError(f"Invalid plan type: {plan_type}")
        
        async with get_db() as db:
            # Get plan from database
            result = await db.execute(
                select(SubscriptionPlan).where(SubscriptionPlan.name == plan_details["name"])
            )
            
            plan = result.scalar_one_or_none()
            
            if not plan:
                logger.warning(f"Plan not found in database: {plan_details['name']}. Creating it now.")
                # Create the plan if it doesn't exist
                plan = SubscriptionPlan(
                    name=plan_details["name"],
                    description=f"{plan_details['name']} subscription plan",
                    price=plan_details["price"] * 100,  # Convert to paise as per model
                    duration_days=plan_details["duration_days"],
                    features=plan_details["features"],  # Model already expects a JSON/dict object
                    is_active=True
                )
                db.add(plan)
                await db.flush()
            
            # Create pending payment record
            payment = Payment(
                user_id=user_id,
                subscription_id=None,  # Will be updated after subscription is created
                amount=plan_details["price"] * 100,  # Convert to paise as per model
                currency="INR",
                payment_id=payment_link_id,  # Will be updated after payment is complete
                order_id=order_id,
                status="pending",
                payment_method="razorpay"
            )
            
            db.add(payment)
            await db.commit()
            
            logger.info(f"Created pending payment record for user {user_id}, order {order_id}")
            return payment.id
            
    except Exception as e:
        logger.error(f"Error creating pending payment in database: {str(e)}")
        return None

async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment verification callback"""

    print("payment_callback")
    query = update.callback_query
    await query.answer()
    
    # Extract order ID from callback data
    callback_parts = query.data.split("_")
    if len(callback_parts) < 3 or callback_parts[1] != "check":
        await query.edit_message_text("Invalid payment request. Please start over with /start command.")
        return
    
    order_id = callback_parts[2]
    
    # Verify payment status with Razorpay
    try:
        # Fetch order from Razorpay
        order = client.order.fetch(order_id)
        
        # Check if payment is successful
        if order["status"] == "paid":
            # Payment successful - create subscription in database
            plan_type = context.user_data.get("selected_plan")
            user_id = context.user_data.get("db_user_id")
            
            subscription_id = await create_subscription_in_db(user_id, plan_type, order_id)
            
            if subscription_id:
                # Payment successful
                # Get selected plan
                plan_details = SUBSCRIPTION_PLANS.get(plan_type)
                
                # Set user as subscribed in context
                context.user_data["is_subscribed"] = True
                context.user_data["subscription_plan"] = plan_type
                
                # Send success message
                success_text = (
                    "🎉 *Payment Successful!*\n\n"
                    f"Thank you for subscribing to our {plan_details['name']} plan.\n"
                    f"Your subscription is now active for {plan_details['duration_days']} days.\n\n"
                    "Next step: Please upload your resume to start receiving personalized job updates."
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
                ])
                
                await query.edit_message_text(
                    success_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                # Error creating subscription
                await query.edit_message_text(
                    "Your payment was successful, but there was an error activating your subscription. "
                    "Please contact support for assistance.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🤝 Support", callback_data="support")],
                        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
                    ])
                )
        else:
            # Payment not yet completed
            await query.edit_message_text(
                "Your payment is not yet complete. Please complete the payment process.\n\n"
                "If you've already paid, it may take a few moments to reflect in our system. "
                "You can check again in a minute.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Check Again", callback_data=f"payment_check_{order_id}")],
                    [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
                ])
            )
    
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        await query.edit_message_text(
            "There was an error verifying your payment. If you've completed the payment, "
            "please contact support for assistance.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤝 Support", callback_data="support")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
            ])
        )

async def create_subscription_in_db(user_id: int, plan_type: str, order_id: str = None):
    """Create a subscription record in the database"""
    try:
        if not user_id:
            logger.error("Cannot create subscription: user_id is None")
            return None
            
        plan_details = SUBSCRIPTION_PLANS.get(plan_type)
        if not plan_details:
            raise ValueError(f"Invalid plan type: {plan_type}")
        
        async with get_db() as db:
            # Get plan from database
            result = await db.execute(
                select(SubscriptionPlan).where(SubscriptionPlan.name == plan_details["name"])
            )
            
            plan = result.scalar_one_or_none()
            
            if not plan:
                logger.warning(f"Plan not found in database: {plan_details['name']}. Creating it now.")
                # Create the plan if it doesn't exist
                plan = SubscriptionPlan(
                    name=plan_details["name"],
                    description=f"{plan_details['name']} subscription plan",
                    price=plan_details["price"] * 100,  # Convert to paise as per model
                    duration_days=plan_details["duration_days"],
                    features=plan_details["features"],  # Model already expects a JSON/dict object
                    is_active=True
                )
                db.add(plan)
                await db.flush()
            
            # Create subscription
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=plan_details["duration_days"])
            
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan.id,
                start_date=start_date,
                end_date=end_date,
                is_active=True,
                is_trial=False,
                subscription_metadata={"source": "telegram_bot"}
            )
            
            db.add(subscription)
            await db.flush()
            
            # If order_id provided, update the payment record
            if order_id:
                # Find existing pending payment record
                payment_result = await db.execute(
                    select(Payment).where(
                        Payment.user_id == user_id,
                        Payment.order_id == order_id,
                        Payment.status == "pending"
                    )
                )
                
                payment = payment_result.scalar_one_or_none()
                
                if payment:
                    # Update existing payment record
                    payment.subscription_id = subscription.id
                    payment.status = "captured"
                    logger.info(f"Updated payment record {payment.id} for subscription {subscription.id}")
                else:
                    # Create new payment record if not found
                    payment = Payment(
                        user_id=user_id,
                        subscription_id=subscription.id,
                        amount=plan.price,  # Already in paise in the database
                        currency="INR",
                        payment_id=f"payment_{datetime.utcnow().timestamp()}",
                        order_id=order_id,
                        status="captured",
                        payment_method="razorpay"
                    )
                    
                    db.add(payment)
                    logger.info(f"Created new payment record for subscription {subscription.id}")
            
            await db.commit()
            
            logger.info(f"Created subscription {subscription.id} for user {user_id}")
            return subscription.id
            
    except Exception as e:
        logger.error(f"Error creating subscription in database: {str(e)}")
        return None

async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Legacy function to maintain compatibility - replaced by process_user_info"""
    # This function is kept for backward compatibility
    # The functionality is now handled by the step-by-step user_info collection
    return await process_user_info(update, context)