# bot/run.py
import asyncio
import logging
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.bot import TelegramBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/bot.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Initialize and run the Telegram bot"""
    try:
        logger.info("Starting Telegram bot")
        
        # Create bot instance
        bot = TelegramBot()
        
        # Run the bot
        bot.run()
        
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()