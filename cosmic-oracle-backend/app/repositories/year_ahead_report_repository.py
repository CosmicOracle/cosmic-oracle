# app/repositories/report_repository.py
"""
Repository for managing user-generated reports.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List

from app.models.orm_models import UserAstrologicalReport

def create_pending_report(db: Session, user_id: int, report_type: str, input_data: Dict[str, Any]) -> UserAstrologicalReport:
    """Creates a new report record with a 'pending' status."""
    report = UserAstrologicalReport(
        user_id=user_id, report_type=report_type,
        status='pending', input_data=input_data
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def find_report_by_id(db: Session, report_id: int) -> Optional[UserAstrologicalReport]:
    """Finds a report by its primary key."""
    return db.query(UserAstrologicalReport).filter_by(id=report_id).first()

def find_reports_by_user(db: Session, user_id: int) -> List[UserAstrologicalReport]:
    """Finds all reports for a given user."""
    return db.query(UserAstrologicalReport).filter_by(user_id=user_id).order_by(UserAstrologicalReport.created_at.desc()).all()

def update_report_as_completed(db: Session, report_id: int, file_identifier: str):
    """Updates a report's status to 'completed' and saves the file path."""
    report = find_report_by_id(db, report_id)
    if report:
        report.status = 'completed'
        report.file_identifier = file_identifier
        report.completed_at = datetime.utcnow()
        db.commit()

def update_report_as_failed(db: Session, report_id: int, error_message: str):
    """Updates a report's status to 'failed' and logs the error."""
    report = find_report_by_id(db, report_id)
    if report:
        report.status = 'failed'
        report.error_message = error_message
        db.commit()

def delete_report_by_id(db: Session, report_id: int) -> bool:
    """Deletes a report record from the database."""
    report = find_report_by_id(db, report_id)
    if report:
        db.delete(report)
        db.commit()
        return True
    return False