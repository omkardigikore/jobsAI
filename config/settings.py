# config/settings.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp"
LOGS_DIR = BASE_DIR / "logs"

# Ensure required directories exist
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Application settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Database settings
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "job_bot_db")

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Redis settings - with fallbacks to environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")

# Razorpay settings
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://fde69b12781f.ngrok.app/")

# AI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "claude")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# Jobs API settings
JOBS_API_KEY = os.getenv("JOBS_API_KEY", "sk-live-P8FmXB3gKD0MQpPw9AsMfmkCnj8iqPlCyKmWF1Ok")
JOBS_API_BASE_URL = os.getenv("JOBS_API_BASE_URL", "https://jobs.indianapi.in")

# Admin settings
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Celery settings
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TIMEZONE = "Asia/Kolkata"

# Job update settings
JOB_UPDATES_PER_DAY = int(os.getenv("JOB_UPDATES_PER_DAY", "2"))
JOB_UPDATE_MORNING_HOUR = int(os.getenv("JOB_UPDATE_MORNING_HOUR", "9"))
JOB_UPDATE_EVENING_HOUR = int(os.getenv("JOB_UPDATE_EVENING_HOUR", "17"))

# API settings
API_PREFIX = "/api/v1"
API_TITLE = "Job Updates Bot API"
API_DESCRIPTION = "API for Job Updates Telegram Bot"
API_VERSION = "1.0.0"

# CORS settings
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

# Security settings
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 60 * 24  # 24 hours in minutes