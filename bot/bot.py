# bot/bot.py
import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config.settings import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)

# Global bot instance
_bot_instance = None

def get_bot_instance():
    """
    Get the global bot instance
    
    Returns:
        Telegram bot instance
    """
    global _bot_instance
    
    if _bot_instance is None:
        from telegram.ext import Application
        from config.settings import TELEGRAM_BOT_TOKEN
        
        # Create application instance
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        _bot_instance = application.bot
    
    return _bot_instance

def set_bot_instance(bot):
    """
    Set the global bot instance
    
    Args:
        bot: Telegram bot instance
    """
    global _bot_instance
    _bot_instance = bot

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Set global bot instance
        set_bot_instance(self.application.bot)
        
        self._register_handlers()
        logger.info("Telegram bot initialized")

    # def _register_handlers(self):
    #     # Import handlers here to avoid circular imports
    #     from bot.handlers.start import start_command, start_callback
    #     from bot.handlers.subscription import (
    #         subscription_callback, 
    #         plan_selected_callback, 
    #         back_to_main_callback,
    #         about_callback
    #     )
    #     from bot.handlers.support import support_callback, exit_support_callback
    #     from bot.handlers.payment import process_email, payment_callback
    #     from bot.handlers.resume import (
    #         resume_upload_callback,
    #         resume_upload_handler,
    #         resume_request_callback,
    #         view_jobs_callback
    #     )
        
    #     # Command handlers
    #     self.application.add_handler(CommandHandler("start", start_command))
    #     self.application.add_handler(CommandHandler("help", self._help_command))
        
    #     # Callback query handlers - menu navigation
    #     self.application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
        
    #     # Subscription handlers
    #     self.application.add_handler(CallbackQueryHandler(subscription_callback, pattern="^subscription$"))
    #     self.application.add_handler(CallbackQueryHandler(plan_selected_callback, pattern="^plan_"))
    #     self.application.add_handler(CallbackQueryHandler(payment_callback, pattern="^payment_check_"))
        
    #     # About handler
    #     self.application.add_handler(CallbackQueryHandler(about_callback, pattern="^about$"))
        
    #     # Support handlers
    #     self.application.add_handler(CallbackQueryHandler(support_callback, pattern="^support$"))
    #     self.application.add_handler(CallbackQueryHandler(exit_support_callback, pattern="^exit_support$"))
        
    #     # Resume handlers
    #     self.application.add_handler(CallbackQueryHandler(resume_upload_callback, pattern="^upload_resume$"))
    #     self.application.add_handler(CallbackQueryHandler(resume_request_callback, pattern="^resume_request_"))
    #     self.application.add_handler(CallbackQueryHandler(view_jobs_callback, pattern="^view_jobs$"))
    #     self.application.add_handler(CallbackQueryHandler(view_jobs_callback, pattern="^load_more_jobs$"))
        
    #     # Document handler for resume uploads
    #     self.application.add_handler(MessageHandler(filters.ATTACHMENT, resume_upload_handler))
        
    #     # Fallback callback handler - must be last callback handler
    #     self.application.add_handler(CallbackQueryHandler(self._default_callback))
        
    #     # Message handlers
    #     self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler))
        
    #     # Error handler
    #     self.application.add_error_handler(self._error_handler)

    def _register_handlers(self):
        # Import handlers here to avoid circular imports
        from bot.handlers.start import start_command, start_callback
        from bot.handlers.subscription import (
            subscription_callback, 
            plan_selected_callback, 
            back_to_main_callback,
            about_callback
        )
        from bot.handlers.support import support_callback, exit_support_callback
        from bot.handlers.payment import (
            process_user_info, 
            payment_callback, 
            confirm_payment_callback,
            edit_info_callback
        )
        from bot.handlers.resume import (
            resume_upload_callback,
            resume_upload_handler,
            resume_request_callback,
            view_jobs_callback
        )
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        
        # Callback query handlers - menu navigation
        self.application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
        
        # Subscription handlers
        self.application.add_handler(CallbackQueryHandler(subscription_callback, pattern="^subscription$"))
        self.application.add_handler(CallbackQueryHandler(plan_selected_callback, pattern="^plan_"))
        
        # Payment handlers
        self.application.add_handler(CallbackQueryHandler(payment_callback, pattern="^payment_check_"))
        self.application.add_handler(CallbackQueryHandler(confirm_payment_callback, pattern="^confirm_payment$"))
        self.application.add_handler(CallbackQueryHandler(edit_info_callback, pattern="^edit_info$"))
        
        # About handler
        self.application.add_handler(CallbackQueryHandler(about_callback, pattern="^about$"))
        
        # Support handlers
        self.application.add_handler(CallbackQueryHandler(support_callback, pattern="^support$"))
        self.application.add_handler(CallbackQueryHandler(exit_support_callback, pattern="^exit_support$"))
        
        # Resume handlers
        self.application.add_handler(CallbackQueryHandler(resume_upload_callback, pattern="^upload_resume$"))
        self.application.add_handler(CallbackQueryHandler(resume_request_callback, pattern="^resume_request_"))
        self.application.add_handler(CallbackQueryHandler(view_jobs_callback, pattern="^view_jobs$"))
        self.application.add_handler(CallbackQueryHandler(view_jobs_callback, pattern="^load_more_jobs$"))
        
        # Document handler for resume uploads
        self.application.add_handler(MessageHandler(filters.ATTACHMENT, resume_upload_handler))
        
        # Fallback callback handler - must be last callback handler
        self.application.add_handler(CallbackQueryHandler(self._default_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler))
        
        # Error handler
        self.application.add_error_handler(self._error_handler)
    
    async def _help_command(self, update, context):
        help_text = (
            "🤖 *Job Updates Bot Help*\n\n"
            "Here are the commands you can use:\n"
            "/start - Start the bot and see main menu\n"
            "/help - Show this help message\n\n"
            "You can also use the buttons in the main menu to:\n"
            "• Subscribe to job updates\n"
            "• Upload your resume\n"
            "• Get customized resumes for specific jobs\n"
            "• Contact support\n\n"
            "If you have any questions, use the Support button in the main menu."
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def _default_callback(self, update, context):
        """Default handler for callback queries"""
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("This functionality is not yet implemented.")
    
    async def _message_handler(self, update, context):
        """Default handler for text messages"""
        # Check if we're in support chat mode
        if context.user_data.get("support_mode"):
            from bot.handlers.support import support_message_handler
            await support_message_handler(update, context)
            return
        
        # Check if we're waiting for user info
        if context.user_data.get("waiting_for_info", False):
            from bot.handlers.payment import process_user_info
            handled = await process_user_info(update, context)
            if handled:
                return
        
        # Default message for unhandled text
        await update.message.reply_text(
            "I'm not sure how to respond to that message. Please use the buttons or commands to interact with me."
        )
    
    async def _error_handler(self, update, context):
        logger.error(f"Update {update} caused error: {context.error}")
        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text(
                "Sorry, something went wrong processing your request. Please try again later."
            )
    
    def run(self):
        logger.info("Starting Telegram bot")
        self.application.run_polling()