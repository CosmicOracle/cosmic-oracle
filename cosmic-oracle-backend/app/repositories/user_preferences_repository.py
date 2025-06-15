# app/repositories/user_preferences_repository.py
"""
Repository for managing User Astrology Preferences.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.orm_models import AstrologyPreference
import json

def find_or_create(db: Session, user_id: int) -> AstrologyPreference:
    """Finds a user's preference record, creating a default one if it doesn't exist."""
    pref = db.query(AstrologyPreference).filter_by(user_id=user_id).first()
    if not pref:
        pref = AstrologyPreference(user_id=user_id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref

def update(db: Session, user_id: int, new_settings: Dict[str, Any]) -> AstrologyPreference:
    """Updates a user's preference record."""
    pref = find_or_create(db, user_id)
    for key, value in new_settings.items():
        if hasattr(pref, key):
            # Handle JSON fields specifically
            if key == 'custom_orbs' and isinstance(value, dict):
                setattr(pref, 'custom_orbs_json', json.dumps(value))
            elif key == 'major_asteroids_list' and isinstance(value, list):
                setattr(pref, 'major_asteroids_list', ",".join(value))
            else:
                setattr(pref, key, value)
    db.commit()
    db.refresh(pref)
    return pref