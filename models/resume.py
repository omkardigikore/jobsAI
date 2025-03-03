# models/resume.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.base import Base

class ResumeRequest(Base):
    __tablename__ = "resume_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(255), nullable=False)  # ID of the job from your API
    request_id = Column(String(255), default=lambda: str(uuid.uuid4()), unique=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    original_resume = Column(Text, nullable=True)  # Original resume content
    customized_resume = Column(Text, nullable=True)  # Customized resume content
    ai_model_used = Column(String(100), nullable=True)  # Which AI model was used
    processing_time = Column(Integer, nullable=True)  # Processing time in seconds
    
    # Relationships
    user = relationship("User", backref="resume_requests")
    
    def __repr__(self):
        return f"<ResumeRequest request_id={self.request_id}, status={self.status}>"