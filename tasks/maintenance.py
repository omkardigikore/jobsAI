# tasks/maintenance.py
import logging
import asyncio
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

from config.celery import app
from config.settings import TEMP_DIR, LOGS_DIR

logger = logging.getLogger(__name__)

@app.task
def cleanup_temp_files():
    """
    Celery task to clean up temporary files
    This is a wrapper that calls the async function
    """
    asyncio.run(_cleanup_temp_files_async())

async def _cleanup_temp_files_async():
    """
    Async implementation of the cleanup task
    Removes temporary files older than 24 hours
    """
    logger.info("Starting temporary files cleanup task")
    
    try:
        # Calculate the cutoff time (24 hours ago)
        cutoff_time = time.time() - (24 * 60 * 60)
        
        # Clean up temp directory
        temp_dir = Path(TEMP_DIR)
        
        if temp_dir.exists():
            cleaned_count = 0
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    # Check file modification time
                    mtime = file_path.stat().st_mtime
                    
                    if mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                        except Exception as e:
                            logger.error(f"Error deleting file {file_path}: {str(e)}")
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
        
        # Clean up old log files (older than 7 days)
        logs_dir = Path(LOGS_DIR)
        log_cutoff_time = time.time() - (7 * 24 * 60 * 60)
        
        if logs_dir.exists():
            cleaned_logs = 0
            
            for file_path in logs_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.log':
                    # Check file modification time
                    mtime = file_path.stat().st_mtime
                    
                    if mtime < log_cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_logs += 1
                        except Exception as e:
                            logger.error(f"Error deleting log file {file_path}: {str(e)}")
            
            logger.info(f"Cleaned up {cleaned_logs} old log files")
    
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")

@app.task
def vacuum_database():
    """
    Perform database vacuum to optimize performance
    """
    asyncio.run(_vacuum_database_async())

async def _vacuum_database_async():
    """
    Async implementation of database vacuum task
    """
    logger.info("Starting database vacuum task")
    
    try:
        from utils.db import get_db
        
        async with get_db() as db:
            # Using raw SQL to perform vacuum
            await db.execute("VACUUM ANALYZE")
            
            logger.info("Database vacuum completed successfully")
    
    except Exception as e:
        logger.error(f"Error in database vacuum task: {str(e)}")