# app/repositories/birth_chart_repository.py
"""
Repository for managing BirthChart records in the database.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import date, time

from app.models.orm_models import BirthChart

def find_by_user_id(db: Session, user_id: int) -> Optional[BirthChart]:
    """Finds a user's existing birth chart."""
    return db.query(BirthChart).filter(BirthChart.user_id == user_id).first()

def create_or_update_chart(
    db: Session,
    user_id: int,
    birth_date: date,
    birth_time: time,
    birth_location: str,
    latitude: float,
    longitude: float,
    chart_data: Dict[str, Any],
    interpretations: Dict[str, Any]
) -> BirthChart:
    """Creates a new birth chart or updates an existing one for a user."""
    existing_chart = find_by_user_id(db, user_id)
    
    if existing_chart:
        # Update existing record
        existing_chart.birth_date = birth_date
        existing_chart.birth_time = birth_time
        existing_chart.birth_location = birth_location
        existing_chart.latitude = latitude
        existing_chart.longitude = longitude
        existing_chart.chart_data = chart_data
        existing_chart.interpretations = interpretations
        chart_to_save = existing_chart
    else:
        # Create new record
        chart_to_save = BirthChart(
            user_id=user_id,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_location=birth_location,
            latitude=latitude,
            longitude=longitude,
            chart_data=chart_data,
            interpretations=interpretations
        )
        db.add(chart_to_save)
    
    db.commit()
    db.refresh(chart_to_save)
    return chart_to_save

def delete_chart_for_user(db: Session, user_id: int) -> bool:
    """Deletes a birth chart for a user. Returns True if successful."""
    chart = find_by_user_id(db, user_id)
    if chart:
        db.delete(chart)
        db.commit()
        return True
    return False