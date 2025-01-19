# app/services/subscription_logic.py
from sqlalchemy.orm import Session
from app import models

def activate_subscription(db: Session, user_id: int, plan: str, stripe_sub_id: str):
    """
    Mark a subscription as active in the DB (or create if it doesn't exist).
    """
    sub = db.query(models.Subscription).filter_by(user_id=user_id).first()
    if not sub:
        sub = models.Subscription(user_id=user_id)

    sub.plan_name = plan
    sub.stripe_subscription_id = stripe_sub_id
    sub.current_status = "active"

    db.add(sub)
    db.commit()
    db.refresh(sub)

def mark_subscription_past_due(db: Session, user_id: int):
    """
    Mark subscription as 'past_due' or similar if payment fails.
    """
    sub = db.query(models.Subscription).filter_by(user_id=user_id).first()
    if sub:
        sub.current_status = "past_due"
        db.add(sub)
        db.commit()
        db.refresh(sub)

def cancel_subscription(db: Session, user_id: int):
    """
    Mark subscription as canceled/unpaid. 
    Optionally call Stripe's API to actually cancel the subscription on Stripe.
    """
    sub = db.query(models.Subscription).filter_by(user_id=user_id).first()
    if sub:
        sub.current_status = "canceled"
        db.add(sub)
        db.commit()
        db.refresh(sub)