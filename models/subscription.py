# models/subscription.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Price in lowest currency unit (e.g., paise for INR)
    duration_days = Column(Integer, nullable=False)
    features = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan name={self.name}, price={self.price/100}>"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    subscription_metadata = Column(JSON, nullable=True)  # Changed from 'metadata' to 'subscription_metadata'
    
    # Relationships
    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.end_date
    
    @property
    def days_remaining(self):
        if self.is_expired:
            return 0
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)
    
    def __repr__(self):
        return f"<Subscription user_id={self.user_id}, plan={self.plan.name if self.plan else None}>"