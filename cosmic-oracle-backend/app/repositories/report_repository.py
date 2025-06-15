# app/repositories/report_repository.py
"""
Repository for managing UserAstrologicalReport records.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.models.orm_models import UserAstrologicalReport

def create_pending_report(db: Session, user_id: int, report_type: str, input_data: Dict[str, Any]) -> UserAstrologicalReport:
    """Creates a new report record with a 'pending' status."""
    report = UserAstrologicalReport(
        user_id=user_id,
        report_type=report_type,
        status='pending',
        input_data=input_data # Store the request data for the background task
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def update_report_status_to_completed(db: Session, report_id: int, file_identifier: str) -> Optional[UserAstrologicalReport]:
    """Updates a report's status to 'completed' and saves the file path."""
    report = db.query(UserAstrologicalReport).filter_by(id=report_id).first()
    if report:
        report.status = 'completed'
        report.file_identifier = file_identifier
        db.commit()
        db.refresh(report)
    return report

def update_report_status_to_failed(db: Session, report_id: int, error_message: str):
    """Updates a report's status to 'failed' and logs the error."""
    report = db.query(UserAstrologicalReport).filter_by(id=report_id).first()
    if report:
        report.status = 'failed'
        report.error_message = error_message
        db.commit()

def find_report_by_id_and_user(db: Session, report_id: int, user_id: int) -> Optional[UserAstrologicalReport]:
    """Finds a specific report belonging to a user."""
    return db.query(UserAstrologicalReport).filter_by(id=report_id, user_id=user_id).first()