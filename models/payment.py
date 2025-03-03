# models/payment.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    amount = Column(Integer, nullable=False)  # Amount in lowest currency unit
    currency = Column(String(10), default="INR")
    payment_id = Column(String(255), unique=True, index=True, nullable=True)  # Razorpay payment ID
    order_id = Column(String(255), unique=True, index=True, nullable=True)  # Razorpay order ID
    status = Column(String(50), nullable=False)  # created, authorized, captured, failed, refunded
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    payment_method = Column(String(50), nullable=True)  # card, netbanking, upi, etc.
    payment_details = Column(JSON, nullable=True)  # Additional payment details
    
    # Relationships
    user = relationship("User", backref="payments")
    subscription = relationship("Subscription", backref="payments")
    
    def __repr__(self):
        return f"<Payment payment_id={self.payment_id}, status={self.status}>"