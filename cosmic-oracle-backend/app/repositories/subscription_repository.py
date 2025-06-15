# app/repositories/subscription_repository.py
"""
Repository for managing User and Subscription data.
"""
from sqlalchemy.orm import Session
from typing import Optional

from app.models.orm_models import User, UserSubscription

def find_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def find_user_by_stripe_customer_id(db: Session, customer_id: str) -> Optional[User]:
    return db.query(User).filter(User.stripe_customer_id == customer_id).first()

def find_subscription_by_stripe_id(db: Session, stripe_subscription_id: str) -> Optional[UserSubscription]:
    return db.query(UserSubscription).filter(UserSubscription.stripe_subscription_id == stripe_subscription_id).first()

def create_or_update_subscription(db: Session, user: User, sub_data: dict) -> UserSubscription:
    """Creates or updates a user's subscription record."""
    subscription = user.subscription
    if not subscription:
        subscription = UserSubscription(user_id=user.id)
        db.add(subscription)
    
    for key, value in sub_data.items():
        setattr(subscription, key, value)
    
    # Update user's stripe_customer_id if it's new
    if user.stripe_customer_id != sub_data.get('stripe_customer_id'):
        user.stripe_customer_id = sub_data.get('stripe_customer_id')

    db.commit()
    db.refresh(subscription)
    return subscription

def update_user_access_level(db: Session, user_id: int, plan_key: str):
    """Updates a user's plan/access level."""
    user = find_user_by_id(db, user_id)
    if user:
        user.plan_key = plan_key
        db.commit()