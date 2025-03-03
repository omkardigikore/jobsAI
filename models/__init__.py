# models/__init__.py
# This file ensures that models package is importable

# Import all models here to make them available when importing models package
from models.base import Base
from models.user import User
from models.subscription import SubscriptionPlan, Subscription
from models.payment import Payment
from models.resume import ResumeRequest
from models.job import SavedJob, JobListing, JobApplication, JobMatch, JobSearchPreference

# Create empty init files for other directories
# utils/__init__.py
# Empty file to make utils a proper package

# ai/__init__.py
# Empty file to make ai a proper package

# ai/agents/__init__.py
# Empty file to make ai.agents a proper package

# bot/__init__.py
# Empty file to make bot a proper package

# bot/handlers/__init__.py
# Empty file to make bot.handlers a proper package

# api/__init__.py
# Empty file to make api a proper package

# api/routes/__init__.py
# Empty file to make api.routes a proper package

# tasks/__init__.py
# Empty file to make tasks a proper package

# scripts/__init__.py
# Empty file to make scripts a proper package