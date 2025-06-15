# app/repositories/numerology_repository.py
"""
Numerology Repository

This module handles all direct database interactions for saved numerology reports.
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date

from app.models.orm_models import NumerologyReport

def save_report(db: Session, user_id: int, full_name: str, birth_date: date, report_numbers: Dict[str, int]) -> NumerologyReport:
    """Creates and saves a new numerology report to the database."""
    new_report = NumerologyReport(
        user_id=user_id,
        full_name_used=full_name,
        birth_date_used=birth_date,
        life_path_number=report_numbers.get("life_path_number"),
        expression_number=report_numbers.get("expression_number"),
        soul_urge_number=report_numbers.get("soul_urge_number"),
        personality_number=report_numbers.get("personality_number"),
        birthday_number=report_numbers.get("birthday_number")
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

def find_all_by_user_id(db: Session, user_id: int) -> List[NumerologyReport]:
    """Retrieves all saved numerology reports for a user."""
    return db.query(NumerologyReport).filter(NumerologyReport.user_id == user_id).order_by(NumerologyReport.created_at.desc()).all()

def find_by_id_and_user_id(db: Session, report_id: int, user_id: int) -> Optional[NumerologyReport]:
    """Retrieves a single saved report by its ID, ensuring it belongs to the correct user."""
    return db.query(NumerologyReport).filter(NumerologyReport.id == report_id, NumerologyReport.user_id == user_id).first()

def delete_by_id(db: Session, report: NumerologyReport):
    """Deletes a given report record from the database."""
    db.delete(report)
    db.commit()