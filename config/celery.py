# # config/celery.py
# import os
# import sys
# from celery import Celery
# from celery.schedules import crontab
# from datetime import timezone, timedelta

# # Add the project root to Python path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Import settings without circular imports
# from config.settings import (
#     CELERY_BROKER_URL,
#     CELERY_RESULT_BACKEND,
#     CELERY_TIMEZONE,
#     JOB_UPDATE_MORNING_HOUR,
#     JOB_UPDATE_EVENING_HOUR
# )

# # Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('PYTHONPATH', '.')

# # Create Celery app
# app = Celery('job_bot')

# # Configure Celery
# app.conf.broker_url = CELERY_BROKER_URL
# app.conf.result_backend = CELERY_RESULT_BACKEND
# app.conf.timezone = CELERY_TIMEZONE

# # Load tasks from these modules
# app.conf.imports = [
#     'tasks.job_updates',
#     'tasks.subscription_alerts',
#     'tasks.maintenance'
# ]

# # Define periodic tasks
# app.conf.beat_schedule = {
#     'send-morning-job-updates': {
#         'task': 'tasks.job_updates.send_job_updates',
#         'schedule': crontab(hour=JOB_UPDATE_MORNING_HOUR, minute=0),
#     },
#     'send-evening-job-updates': {
#         'task': 'tasks.job_updates.send_job_updates',
#         'schedule': crontab(hour=JOB_UPDATE_EVENING_HOUR, minute=0),
#     },
#     'send-daily-job-digest': {
#         'task': 'tasks.job_updates.send_daily_job_digest',
#         'schedule': crontab(hour=12, minute=0),
#     },
#     'update-job-database': {
#         'task': 'tasks.job_updates.update_job_database',
#         'schedule': crontab(minute=0, hour='*/1'),  # Every hour
#     },
#     'check-subscriptions-expiry': {
#         'task': 'tasks.subscription_alerts.check_expiring_subscriptions',
#         'schedule': crontab(hour=10, minute=0),  # Once a day at 10 AM
#     },
#     'cleanup-temp-files': {
#         'task': 'tasks.maintenance.cleanup_temp_files',
#         'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
#     },
# }

# # Other Celery configurations
# app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json',
#     task_acks_late=True,
#     task_reject_on_worker_lost=True,
#     worker_prefetch_multiplier=1,
#     worker_max_tasks_per_child=1000,
#     task_ignore_result=True,
#     task_store_errors_even_if_ignored=True,
# )

# if __name__ == '__main__':
#     app.start()



# config/celery.py
import os
import sys
from celery import Celery
from celery.schedules import crontab
from datetime import timezone, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings
from config.settings import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CELERY_TIMEZONE,
    JOB_UPDATE_MORNING_HOUR,
    JOB_UPDATE_EVENING_HOUR,
    REDIS_URL,
    REDIS_HOST,
    REDIS_PORT
)

# Set environment variables
os.environ.setdefault('PYTHONPATH', '.')

# Print Redis connection details for debugging
print(f"Celery using broker URL: {CELERY_BROKER_URL}")
print(f"Redis host: {REDIS_HOST}, port: {REDIS_PORT}")
print(f"Redis URL: {REDIS_URL}")

# Create Celery app
app = Celery('job_bot')

# Configure Celery with explicit broker URL
app.conf.broker_url = REDIS_URL
app.conf.result_backend = REDIS_URL

# Set timezone
app.conf.timezone = CELERY_TIMEZONE

# Load tasks from these modules (commented out until we have the modules)
app.conf.imports = [
    'tasks.job_updates',
    'tasks.subscription_alerts',
    'tasks.maintenance'
]

# Define periodic tasks (commented out until we have the task modules)
# app.conf.beat_schedule = {
#     'send-morning-job-updates': {
#         'task': 'tasks.job_updates.send_job_updates',
#         'schedule': crontab(hour=JOB_UPDATE_MORNING_HOUR, minute=0),
#     },
#     'send-evening-job-updates': {
#         'task': 'tasks.job_updates.send_job_updates',
#         'schedule': crontab(hour=JOB_UPDATE_EVENING_HOUR, minute=0),
#     },
# }

# Other Celery configurations
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_ignore_result=True,
    task_store_errors_even_if_ignored=True,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_pool_limit=None,
)

if __name__ == '__main__':
    app.start()