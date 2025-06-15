# app/repositories/tarot_repository.py
"""
Tarot Repository

This module handles all direct database interactions for saved Tarot readings.
It implements the Repository Pattern to decouple the service layer from the database implementation.
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

# Assuming your ORM model is defined here
from app.models.orm_models import SavedTarotReading

def save_reading(
    db: Session, 
    user_id: int, 
    spread_type: str, 
    cards_drawn: List[Dict[str, Any]],
    question_asked: Optional[str] = None, 
    user_notes: Optional[str] = None
) -> SavedTarotReading:
    """Creates and saves a new tarot reading to the database."""
    new_reading = SavedTarotReading(
        user_id=user_id,
        spread_type=spread_type,
        question_asked=question_asked,
        cards_drawn=cards_drawn,
        interpretation_notes=user_notes,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)
    return new_reading

def find_all_by_user_id(db: Session, user_id: int) -> List[SavedTarotReading]:
    """Retrieves all saved tarot readings for a specific user, most recent first."""
    return db.query(SavedTarotReading).filter(SavedTarotReading.user_id == user_id).order_by(SavedTarotReading.created_at.desc()).all()

def find_by_id_and_user_id(db: Session, reading_id: int, user_id: int) -> Optional[SavedTarotReading]:
    """Retrieves a single saved reading by its ID, ensuring it belongs to the correct user."""
    return db.query(SavedTarotReading).filter(
        SavedTarotReading.id == reading_id,
        SavedTarotReading.user_id == user_id
    ).first()

def delete_by_id(db: Session, reading: SavedTarotReading) -> bool:
    """Deletes a given reading record from the database."""
    db.delete(reading)
    db.commit()
    return True