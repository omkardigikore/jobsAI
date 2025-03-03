# models/job.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base

class SavedJob(Base):
    """Model for jobs saved by users"""
    __tablename__ = "saved_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(255), nullable=False)  # ID from the Jobs API
    job_data = Column(JSON, nullable=False)  # Complete job data
    saved_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)  # User notes about the job
    
    __table_args__ = (
        # Unique constraint to prevent duplicate saved jobs
        UniqueConstraint('user_id', 'job_id', name='uix_user_job'),
    )
    
    # Relationships
    user = relationship("User", backref="saved_jobs")
    
    def __repr__(self):
        return f"<SavedJob user_id={self.user_id}, job_id={self.job_id}>"

class JobListing(Base):
    """Model for caching job listings from API"""
    __tablename__ = "job_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), unique=True, index=True, nullable=False)  # ID from the Jobs API
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    job_type = Column(String(100), nullable=True)  # e.g., Full Time, Part Time
    experience = Column(String(100), nullable=True)  # e.g., 1-3 years, 3-5 years
    posted_date = Column(DateTime, nullable=True)
    job_data = Column(JSON, nullable=False)  # Complete job data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<JobListing job_id={self.job_id}, title={self.title}>"

class JobApplication(Base):
    """Model for tracking job applications"""
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(255), nullable=False)  # ID from the Jobs API
    status = Column(String(50), default="applied")  # applied, interview, offer, rejected, etc.
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resume_id = Column(Integer, ForeignKey("resume_requests.id"), nullable=True)  # Changed from resume_request_id
    feedback = Column(Text, nullable=True)  # User feedback about the application
    notes = Column(Text, nullable=True)  # User notes about the application
    job_data = Column(JSON, nullable=True)  # Job data at the time of application
    
    # Relationships
    user = relationship("User", backref="job_applications")
    resume = relationship("ResumeRequest", backref="job_applications")
    
    __table_args__ = (
        # Unique constraint to prevent duplicate applications
        UniqueConstraint('user_id', 'job_id', name='uix_user_job_application'),
    )
    
    def __repr__(self):
        return f"<JobApplication user_id={self.user_id}, job_id={self.job_id}, status={self.status}>"

class JobMatch(Base):
    """Model for storing AI-generated job matches"""
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(255), nullable=False)  # ID from the Jobs API
    match_percentage = Column(Integer, nullable=False)  # 0-100
    match_reasons = Column(Text, nullable=True)  # Reasons for the match
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_to_user = Column(Boolean, default=False)  # Whether this match was sent to the user
    user_feedback = Column(String(50), nullable=True)  # User feedback (e.g., "relevant", "not relevant")
    job_data = Column(JSON, nullable=True)  # Job data at the time of match
    
    # Relationships
    user = relationship("User", backref="job_matches")
    
    __table_args__ = (
        # Unique constraint for user-job combination
        UniqueConstraint('user_id', 'job_id', name='uix_user_job_match'),
    )
    
    def __repr__(self):
        return f"<JobMatch user_id={self.user_id}, job_id={self.job_id}, match_percentage={self.match_percentage}>"

class JobSearchPreference(Base):
    """Model for storing user job search preferences"""
    __tablename__ = "job_search_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    locations = Column(JSON, nullable=True)  # Preferred locations
    job_types = Column(JSON, nullable=True)  # Preferred job types (Full Time, Part Time, etc.)
    min_salary = Column(Integer, nullable=True)  # Minimum expected salary
    max_commute_distance = Column(Integer, nullable=True)  # Maximum commute distance in km
    industries = Column(JSON, nullable=True)  # Preferred industries
    roles = Column(JSON, nullable=True)  # Preferred job roles
    excluded_companies = Column(JSON, nullable=True)  # Companies to exclude
    remote_preference = Column(String(50), nullable=True)  # remote, hybrid, on-site, any
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="job_search_preference")
    
    def __repr__(self):
        return f"<JobSearchPreference user_id={self.user_id}>"