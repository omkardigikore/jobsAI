# # bot/handlers/resume.py
# import logging
# import os
# from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.ext import ContextTypes

# logger = logging.getLogger(__name__)

# async def resume_upload_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle resume upload button click"""
#     query = update.callback_query
#     await query.answer()
    
#     # Check if user is subscribed
#     is_subscribed = context.user_data.get("is_subscribed", False)
    
#     if not is_subscribed:
#         # User is not subscribed, prompt to subscribe first
#         await query.edit_message_text(
#             "You need an active subscription to upload your resume. Please subscribe to a plan first.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")],
#                 [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#             ])
#         )
#         return
    
#     # Prompt user to upload resume
#     await query.edit_message_text(
#         "📤 *Upload Your Resume*\n\n"
#         "Please send your resume as a PDF or DOCX file. We'll analyze it to find the best job matches for you.\n\n"
#         "Your resume should include:\n"
#         "• Contact information\n"
#         "• Work experience\n"
#         "• Education\n"
#         "• Skills\n\n"
#         "For best results, ensure your resume is up-to-date and includes relevant keywords for your target jobs.",
#         parse_mode="Markdown",
#         reply_markup=InlineKeyboardMarkup([
#             [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#         ])
#     )
    
#     # Set flag to indicate waiting for resume
#     context.user_data["waiting_for_resume"] = True

# async def resume_upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle resume document upload"""
#     # Check if user is subscribed and we're waiting for resume
#     is_subscribed = context.user_data.get("is_subscribed", False)
#     waiting_for_resume = context.user_data.get("waiting_for_resume", False)
    
#     if not is_subscribed:
#         await update.message.reply_text(
#             "You need an active subscription to upload your resume. Please subscribe to a plan first.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")]
#             ])
#         )
#         return
    
#     if not waiting_for_resume:
#         await update.message.reply_text(
#             "Please click the 'Upload Resume' button in the main menu to upload your resume."
#         )
#         return
    
#     # Get the document
#     document = update.message.document
    
#     # Check if it's a PDF or DOC/DOCX
#     file_name = document.file_name.lower()
#     if not (file_name.endswith('.pdf') or file_name.endswith('.doc') or file_name.endswith('.docx')):
#         await update.message.reply_text(
#             "Please upload your resume in PDF, DOC, or DOCX format only."
#         )
#         return
    
#     # Send processing message
#     processing_message = await update.message.reply_text("Processing your resume... This may take a minute.")
    
#     try:
#         # In a real implementation, download and process the resume
#         # For now, simulate resume processing
        
#         # Clear waiting flag
#         context.user_data["waiting_for_resume"] = False
        
#         # Set user's resume status
#         context.user_data["has_resume"] = True
#         context.user_data["resume_processed"] = True
        
#         # Simulate resume data
#         context.user_data["resume_data"] = {
#             "skills": ["Python", "JavaScript", "React", "SQL", "Data Analysis"],
#             "experience_years": 3,
#             "education": "Bachelor's in Computer Science",
#             "job_titles": ["Software Developer", "Web Developer"]
#         }
        
#         # Send success message
#         await context.bot.edit_message_text(
#             chat_id=update.effective_chat.id,
#             message_id=processing_message.message_id,
#             text=(
#                 "✅ *Resume Processed Successfully!*\n\n"
#                 "We've analyzed your resume and will match you with relevant job opportunities.\n\n"
#                 "*Key Skills Identified:*\n"
#                 "• Python\n"
#                 "• JavaScript\n"
#                 "• React\n"
#                 "• SQL\n"
#                 "• Data Analysis\n\n"
#                 "You'll now start receiving personalized job updates based on your profile."
#             ),
#             parse_mode="Markdown",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("View Sample Jobs", callback_data="view_jobs")],
#                 [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#             ])
#         )
    
#     except Exception as e:
#         logger.error(f"Error processing resume: {str(e)}")
        
#         # Clear waiting flag
#         context.user_data["waiting_for_resume"] = False
        
#         await context.bot.edit_message_text(
#             chat_id=update.effective_chat.id,
#             message_id=processing_message.message_id,
#             text="❌ There was an error processing your resume. Please try again later.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#             ])
#         )

# async def resume_request_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle custom resume request"""
#     query = update.callback_query
#     await query.answer()
    
#     # Check if user is subscribed
#     is_subscribed = context.user_data.get("is_subscribed", False)
    
#     if not is_subscribed:
#         await query.edit_message_text(
#             "You need an active subscription to request customized resumes. Please subscribe to a plan first.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")]
#             ])
#         )
#         return
    
#     # Check if user has uploaded a resume
#     has_resume = context.user_data.get("has_resume", False)
    
#     if not has_resume:
#         await query.edit_message_text(
#             "You need to upload your resume before requesting a customized version. Please upload your resume first.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")]
#             ])
#         )
#         return
    
#     # Extract job ID from callback data
#     callback_parts = query.data.split("_")
#     if len(callback_parts) < 3 or callback_parts[1] != "request":
#         await query.edit_message_text("Invalid resume request. Please try again.")
#         return
    
#     job_id = callback_parts[2]
    
#     # Send processing message
#     await query.edit_message_text(
#         "🔄 *Processing Resume Request*\n\n"
#         "We're customizing your resume for this job position. This usually takes 3-5 minutes.\n\n"
#         "You'll receive a notification when your customized resume is ready.",
#         parse_mode="Markdown"
#     )
    
#     # In a real implementation, process the resume customization in the background
#     # For now, simulate the processing delay and success
    
#     # Simulate a delay (would be handled by Celery in production)
#     import asyncio
#     await asyncio.sleep(2)
    
#     # Send a new message with the customized resume (simulated)
#     customized_resume_text = (
#         "✅ *Customized Resume Ready*\n\n"
#         "Here's your tailored resume optimized for the selected job position:\n\n"
#         "```\n"
#         "JANE DOE\n"
#         "Email: jane.doe@example.com | Phone: (123) 456-7890\n\n"
#         "PROFESSIONAL SUMMARY\n"
#         "Experienced software developer with 3+ years of expertise in Python, JavaScript, and React. "
#         "Demonstrated success in building scalable web applications and optimizing database performance.\n\n"
#         "SKILLS\n"
#         "• Programming: Python, JavaScript, React, SQL\n"
#         "• Tools: Git, Docker, AWS, Jira\n"
#         "• Soft Skills: Problem-solving, Team collaboration, Agile methodology\n\n"
#         "WORK EXPERIENCE\n"
#         "Software Developer | TechCorp Inc. | 2020-Present\n"
#         "• Developed and maintained web applications using React and Python\n"
#         "• Optimized database queries resulting in 30% performance improvement\n"
#         "• Collaborated with cross-functional teams to deliver projects on time\n\n"
#         "EDUCATION\n"
#         "Bachelor of Science in Computer Science | University of Technology | 2019\n"
#         "```\n\n"
#         "This customized resume highlights your relevant skills and experience for the position. "
#         "You can now use this version when applying for the job."
#     )
    
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=customized_resume_text,
#         parse_mode="Markdown",
#         reply_markup=InlineKeyboardMarkup([
#             [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#         ])
#     )

# async def view_jobs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle View Jobs button"""
#     query = update.callback_query
#     await query.answer()
    
#     # Check if user is subscribed
#     is_subscribed = context.user_data.get("is_subscribed", False)
    
#     if not is_subscribed:
#         await query.edit_message_text(
#             "You need an active subscription to view jobs. Please subscribe to a plan first.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")]
#             ])
#         )
#         return
    
#     # Check if user has uploaded a resume
#     has_resume = context.user_data.get("has_resume", False)
    
#     if not has_resume:
#         await query.edit_message_text(
#             "You need to upload your resume before viewing matched jobs. Please upload your resume first.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")]
#             ])
#         )
#         return
    
#     # Show sample jobs (in a real implementation, these would be fetched from the API)
#     await query.edit_message_text(
#         "🔍 *Matched Jobs*\n\n"
#         "Here are some job openings that match your profile:",
#         parse_mode="Markdown"
#     )
    
#     # Send individual job listings
#     await send_sample_jobs(update, context)

# async def send_sample_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Send sample job listings"""
#     chat_id = update.effective_chat.id
    
#     # Sample job data (in a real implementation, this would come from the API)
#     sample_jobs = [
#         {
#             "id": "job1",
#             "title": "Senior Python Developer",
#             "company": "TechCorp Inc.",
#             "location": "Remote",
#             "description": "We're looking for an experienced Python developer to join our team. You'll work on building and maintaining our cloud-based services.",
#             "match_percentage": 92
#         },
#         {
#             "id": "job2",
#             "title": "Frontend Developer (React)",
#             "company": "WebSolutions Ltd.",
#             "location": "Bangalore",
#             "description": "Join our dynamic team to build responsive and intuitive user interfaces using React.js and modern JavaScript.",
#             "match_percentage": 85
#         }
#     ]
    
#     for job in sample_jobs:
#         job_text = (
#             f"🔍 *{job['title']}*\n\n"
#             f"🏢 *Company:* {job['company']}\n"
#             f"📍 *Location:* {job['location']}\n"
#             f"🔄 *Match:* {job['match_percentage']}%\n\n"
#             f"{job['description']}\n\n"
#         )
        
#         keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("✨ Customize Resume", callback_data=f"resume_request_{job['id']}")],
#             [
#                 InlineKeyboardButton("💾 Save Job", callback_data=f"save_job_{job['id']}"),
#                 InlineKeyboardButton("👎 Not Interested", callback_data=f"not_interested_{job['id']}")
#             ]
#         ])
        
#         await context.bot.send_message(
#             chat_id=chat_id,
#             text=job_text,
#             parse_mode="Markdown",
#             reply_markup=keyboard
#         )
    
#     # Send a "More Jobs" button at the end
#     await context.bot.send_message(
#         chat_id=chat_id,
#         text="Want to see more jobs?",
#         reply_markup=InlineKeyboardMarkup([
#             [InlineKeyboardButton("Load More Jobs", callback_data="load_more_jobs")],
#             [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#         ])
#     )


# bot/handlers/resume.py
import logging
import os
import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from utils.db import get_db
from models.user import User
from models.subscription import Subscription
from sqlalchemy.future import select
from datetime import datetime

logger = logging.getLogger(__name__)

async def check_subscription_in_db(telegram_id):
    """Check if user has active subscription in database"""
    try:
        async with get_db() as db:
            # Get user
            result = await db.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User with telegram_id {telegram_id} not found in database")
                return False, None
            
            # Check for active subscription
            now = datetime.utcnow()
            result = await db.execute(
                select(Subscription).where(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True,
                    Subscription.end_date > now
                )
            )
            
            subscription = result.scalar_one_or_none()
            
            if subscription:
                logger.info(f"Found active subscription for user {user.id}")
                return True, user.id
            else:
                logger.warning(f"No active subscription found for user {user.id}")
                return False, user.id
    
    except Exception as e:
        logger.error(f"Error checking subscription in database: {str(e)}")
        return False, None

async def resume_upload_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle resume upload button click"""
    query = update.callback_query
    await query.answer()
    
    # Check if user is subscribed by querying the database
    telegram_id = update.effective_user.id
    is_subscribed, user_id = await check_subscription_in_db(telegram_id)
    
    # Save user_id in context
    if user_id:
        context.user_data["db_user_id"] = user_id
    
    if not is_subscribed:
        # User is not subscribed, prompt to subscribe first
        await query.edit_message_text(
            "You need an active subscription to upload your resume. Please subscribe to a plan first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
            ])
        )
        return
    
    # Prompt user to upload resume
    await query.edit_message_text(
        "📤 *Upload Your Resume*\n\n"
        "Please send your resume as a PDF or DOCX file. We'll analyze it to find the best job matches for you.\n\n"
        "Your resume should include:\n"
        "• Contact information\n"
        "• Work experience\n"
        "• Education\n"
        "• Skills\n\n"
        "For best results, ensure your resume is up-to-date and includes relevant keywords for your target jobs.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
        ])
    )
    
    # Set flag to indicate waiting for resume
    context.user_data["waiting_for_resume"] = True

async def resume_upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle resume document upload"""
    # Check if user is subscribed by querying the database
    telegram_id = update.effective_user.id
    is_subscribed, user_id = await check_subscription_in_db(telegram_id)
    
    # Save user_id in context
    if user_id:
        context.user_data["db_user_id"] = user_id
    
    # Check if we're waiting for resume
    waiting_for_resume = context.user_data.get("waiting_for_resume", False)
    
    if not is_subscribed:
        await update.message.reply_text(
            "You need an active subscription to upload your resume. Please subscribe to a plan first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")]
            ])
        )
        return
    
    if not waiting_for_resume:
        await update.message.reply_text(
            "Please click the 'Upload Resume' button in the main menu to upload your resume."
        )
        return
    
    # Get the document
    document = update.message.document
    
    # Check if it's a PDF or DOC/DOCX
    file_name = document.file_name.lower()
    if not (file_name.endswith('.pdf') or file_name.endswith('.doc') or file_name.endswith('.docx')):
        await update.message.reply_text(
            "Please upload your resume in PDF, DOC, or DOCX format only."
        )
        return
    
    # Send processing message
    processing_message = await update.message.reply_text("Processing your resume... This may take a minute.")
    
    try:
        # In a real implementation, download and process the resume
        # For now, simulate resume processing
        
        # Clear waiting flag
        context.user_data["waiting_for_resume"] = False
        
        # Set user's resume status in the database
        await update_user_resume_status(user_id, True)
        
        # Simulate resume data
        sample_resume_data = {
            "skills": ["Python", "JavaScript", "React", "SQL", "Data Analysis"],
            "experience_years": 3,
            "education": "Bachelor's in Computer Science",
            "job_titles": ["Software Developer", "Web Developer"]
        }
        
        # Send success message
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_message.message_id,
            text=(
                "✅ *Resume Processed Successfully!*\n\n"
                "We've analyzed your resume and will match you with relevant job opportunities.\n\n"
                "*Key Skills Identified:*\n"
                "• Python\n"
                "• JavaScript\n"
                "• React\n"
                "• SQL\n"
                "• Data Analysis\n\n"
                "You'll now start receiving personalized job updates based on your profile."
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View Sample Jobs", callback_data="view_jobs")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
            ])
        )
    
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        
        # Clear waiting flag
        context.user_data["waiting_for_resume"] = False
        
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_message.message_id,
            text="❌ There was an error processing your resume. Please try again later.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
            ])
        )

async def update_user_resume_status(user_id, has_resume, resume_data=None):
    """Update user's resume status in the database"""
    try:
        async with get_db() as db:
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User with id {user_id} not found in database")
                return False
            
            # Update resume status
            user.has_resume = has_resume
            
            if resume_data:
                user.resume_data = resume_data
            
            await db.commit()
            logger.info(f"Updated resume status for user {user_id}")
            return True
    
    except Exception as e:
        logger.error(f"Error updating user resume status: {str(e)}")
        return False

async def resume_request_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom resume request"""
    query = update.callback_query
    await query.answer()
    
    # Check if user is subscribed by querying the database
    telegram_id = update.effective_user.id
    is_subscribed, user_id = await check_subscription_in_db(telegram_id)
    
    # Save user_id in context
    if user_id:
        context.user_data["db_user_id"] = user_id
    
    if not is_subscribed:
        await query.edit_message_text(
            "You need an active subscription to request customized resumes. Please subscribe to a plan first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")]
            ])
        )
        return
    
    # Check if user has uploaded a resume
    has_resume = await check_user_has_resume(user_id)
    
    if not has_resume:
        await query.edit_message_text(
            "You need to upload your resume before requesting a customized version. Please upload your resume first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")]
            ])
        )
        return
    
    # Extract job ID from callback data
    callback_parts = query.data.split("_")
    if len(callback_parts) < 3 or callback_parts[1] != "request":
        await query.edit_message_text("Invalid resume request. Please try again.")
        return
    
    job_id = callback_parts[2]
    
    # Send processing message
    await query.edit_message_text(
        "🔄 *Processing Resume Request*\n\n"
        "We're customizing your resume for this job position. This usually takes 3-5 minutes.\n\n"
        "You'll receive a notification when your customized resume is ready.",
        parse_mode="Markdown"
    )
    
    # In a real implementation, process the resume customization in the background
    # For now, simulate the processing delay and success
    
    # Simulate a delay (would be handled by Celery in production)
    import asyncio
    await asyncio.sleep(2)
    
    # Send a new message with the customized resume (simulated)
    customized_resume_text = (
        "✅ *Customized Resume Ready*\n\n"
        "Here's your tailored resume optimized for the selected job position:\n\n"
        "```\n"
        "JANE DOE\n"
        "Email: jane.doe@example.com | Phone: (123) 456-7890\n\n"
        "PROFESSIONAL SUMMARY\n"
        "Experienced software developer with 3+ years of expertise in Python, JavaScript, and React. "
        "Demonstrated success in building scalable web applications and optimizing database performance.\n\n"
        "SKILLS\n"
        "• Programming: Python, JavaScript, React, SQL\n"
        "• Tools: Git, Docker, AWS, Jira\n"
        "• Soft Skills: Problem-solving, Team collaboration, Agile methodology\n\n"
        "WORK EXPERIENCE\n"
        "Software Developer | TechCorp Inc. | 2020-Present\n"
        "• Developed and maintained web applications using React and Python\n"
        "• Optimized database queries resulting in 30% performance improvement\n"
        "• Collaborated with cross-functional teams to deliver projects on time\n\n"
        "EDUCATION\n"
        "Bachelor of Science in Computer Science | University of Technology | 2019\n"
        "```\n\n"
        "This customized resume highlights your relevant skills and experience for the position. "
        "You can now use this version when applying for the job."
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=customized_resume_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
        ])
    )

async def check_user_has_resume(user_id):
    """Check if user has uploaded a resume"""
    try:
        async with get_db() as db:
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User with id {user_id} not found in database")
                return False
            
            return user.has_resume
    
    except Exception as e:
        logger.error(f"Error checking if user has resume: {str(e)}")
        return False

async def view_jobs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle View Jobs button"""
    query = update.callback_query
    await query.answer()
    
    # Check if user is subscribed by querying the database
    telegram_id = update.effective_user.id
    is_subscribed, user_id = await check_subscription_in_db(telegram_id)
    
    # Save user_id in context
    if user_id:
        context.user_data["db_user_id"] = user_id
    
    if not is_subscribed:
        await query.edit_message_text(
            "You need an active subscription to view jobs. Please subscribe to a plan first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💼 Subscription Plans", callback_data="subscription")]
            ])
        )
        return
    
    # Check if user has uploaded a resume
    has_resume = await check_user_has_resume(user_id)
    
    if not has_resume:
        await query.edit_message_text(
            "You need to upload your resume before viewing matched jobs. Please upload your resume first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")]
            ])
        )
        return
    
    # Show sample jobs (in a real implementation, these would be fetched from the API)
    await query.edit_message_text(
        "🔍 *Matched Jobs*\n\n"
        "Here are some job openings that match your profile:",
        parse_mode="Markdown"
    )
    
    # Send individual job listings
    await send_sample_jobs(update, context)

async def send_sample_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send sample job listings"""
    chat_id = update.effective_chat.id
    
    # Sample job data (in a real implementation, this would come from the API)
    sample_jobs = [
        {
            "id": "job1",
            "title": "Senior Python Developer",
            "company": "TechCorp Inc.",
            "location": "Remote",
            "description": "We're looking for an experienced Python developer to join our team. You'll work on building and maintaining our cloud-based services.",
            "match_percentage": 92
        },
        {
            "id": "job2",
            "title": "Frontend Developer (React)",
            "company": "WebSolutions Ltd.",
            "location": "Bangalore",
            "description": "Join our dynamic team to build responsive and intuitive user interfaces using React.js and modern JavaScript.",
            "match_percentage": 85
        }
    ]
    
    for job in sample_jobs:
        job_text = (
            f"🔍 *{job['title']}*\n\n"
            f"🏢 *Company:* {job['company']}\n"
            f"📍 *Location:* {job['location']}\n"
            f"🔄 *Match:* {job['match_percentage']}%\n\n"
            f"{job['description']}\n\n"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Customize Resume", callback_data=f"resume_request_{job['id']}")],
            [
                InlineKeyboardButton("💾 Save Job", callback_data=f"save_job_{job['id']}"),
                InlineKeyboardButton("👎 Not Interested", callback_data=f"not_interested_{job['id']}")
            ]
        ])
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=job_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    # Send a "More Jobs" button at the end
    await context.bot.send_message(
        chat_id=chat_id,
        text="Want to see more jobs?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Load More Jobs", callback_data="load_more_jobs")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
        ])
    )