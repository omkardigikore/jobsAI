# models/user.py
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey, Text, JSON, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from models.subscription import Subscription

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    # Change from Integer to BigInteger to handle large Telegram IDs
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    has_resume = Column(Boolean, default=False)
    resume_data = Column(JSON, nullable=True)  # Processed resume data in JSON format
    
    # Relationships
    # subscriptions = relationship("Subscription", back_populates="user", order_by="desc(Subscription.created_at)")
    subscriptions = relationship("Subscription", back_populates="user", order_by=desc(Subscription.created_at))

    payments = relationship("Payment", back_populates="user")
    resume_requests = relationship("ResumeRequest", back_populates="user")
    
    @property
    def has_active_subscription(self):
        return any(subscription.is_active for subscription in self.subscriptions)
    
    @property
    def current_subscription(self):
        active_subs = [sub for sub in self.subscriptions if sub.is_active]
        return active_subs[0] if active_subs else None
    
    def __repr__(self):
        return f"<User telegram_id={self.telegram_id}, name={self.first_name}>"