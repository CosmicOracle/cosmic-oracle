# app/repositories/meditation_repository.py
"""
Repository for managing UserMeditationSession records.
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.orm_models import UserMeditationSession

def create_session(db: Session, user_id: int, start_time: datetime, end_time: datetime, duration: int, meditation_type: str, notes: Optional[str], quality_rating: Optional[int]) -> UserMeditationSession:
    """Creates and saves a new meditation session."""
    session = UserMeditationSession(
        user_id=user_id,
        start_time=start_time,
        end_time=end_time,
        duration=duration,
        meditation_type=meditation_type,
        notes=notes,
        quality_rating=quality_rating
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def find_sessions_for_user(db: Session, user_id: int, start_date: datetime, end_date: datetime, limit: int, offset: int) -> Tuple[List[UserMeditationSession], int]:
    """Retrieves a paginated history of meditation sessions for a user."""
    query = db.query(UserMeditationSession).filter(UserMeditationSession.user_id == user_id)
    if start_date:
        query = query.filter(UserMeditationSession.start_time >= start_date)
    if end_date:
        query = query.filter(UserMeditationSession.start_time <= end_date)
    
    total_count = query.count()
    sessions = query.order_by(UserMeditationSession.start_time.desc()).offset(offset).limit(limit).all()
    return sessions, total_count