# app/tasks/report_year_ahead_report_tasks.py
"""
Background tasks for generating complex reports.
"""
from app.celery_app import celery_app
from app.services.year_ahead_report_service import year_ahead_report_service_instance
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.generate_year_ahead_pdf")
def generate_year_ahead_pdf(report_id: int):
    """Celery task to generate a Year Ahead PDF report asynchronously."""
    logger.info(f"Starting Year Ahead PDF generation task for report_id: {report_id}")
    db = SessionLocal()
    try:
        # The service method does all the heavy lifting
        year_ahead_report_service_instance.generate_and_save_pdf(db, report_id)
        logger.info(f"Successfully completed Year Ahead PDF generation for report_id: {report_id}")
    except Exception as e:
        logger.critical(f"Year Ahead PDF task FAILED for report_id {report_id}: {e}", exc_info=True)
        # The service method itself handles updating the DB status to 'failed'
    finally:
        db.close()