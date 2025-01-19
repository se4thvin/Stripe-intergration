# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Example fields if needed:
    # stripe_customer_id = Column(String, nullable=True)

    # Relationship to subscription(s)
    subscription = relationship("Subscription", back_populates="owner", uselist=False)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    current_status = Column(String, default="inactive")  # e.g. active, past_due, canceled
    plan_name = Column(String, nullable=True)            # e.g. "basic", "premium", "gold"

    owner = relationship("User", back_populates="subscription")