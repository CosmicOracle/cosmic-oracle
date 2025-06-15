# app/repositories/calendar_repository.py
"""
Repository for Astral Calendar and Personal Events.
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.orm_models import PersonalEvent, AstralCalendarSettings

def get_personal_events_for_user(db: Session, user_id: int, start_date: datetime, end_date: datetime) -> List[PersonalEvent]:
    """Retrieves a user's personal events within a date range."""
    return db.query(PersonalEvent).filter(
        PersonalEvent.user_id == user_id,
        PersonalEvent.event_date >= start_date,
        PersonalEvent.event_date <= end_date
    ).order_by(PersonalEvent.event_date).all()

def find_or_create_user_settings(db: Session, user_id: int) -> AstralCalendarSettings:
    """Gets a user's settings, creating default settings if they don't exist."""
    settings = db.query(AstralCalendarSettings).filter_by(user_id=user_id).first()
    if not settings:
        settings = AstralCalendarSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_user_settings(db: Session, user_id: int, settings_data: Dict[str, Any]) -> AstralCalendarSettings:
    """Updates a user's calendar settings."""
    settings = find_or_create_user_settings(db, user_id)
    for key, value in settings_data.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings