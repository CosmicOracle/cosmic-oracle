# app/tasks/report_tasks.py
"""
Background tasks for generating complex reports.
"""
from app.celery_app import celery_app # Assuming you have a celery app instance
from app.services.report_generation_service import report_generation_service_instance
from app.core.database import SessionLocal # To create a new DB session for the task
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.generate_full_report_pdf")
def generate_full_report_pdf(report_id: int):
    """
    Celery task to generate a PDF report asynchronously.
    """
    logger.info(f"Starting PDF generation task for report_id: {report_id}")
    db = SessionLocal()
    try:
        # The service method does all the heavy lifting
        report_generation_service_instance.generate_and_save_pdf(db, report_id)
        logger.info(f"Successfully completed PDF generation for report_id: {report_id}")
    except Exception as e:
        logger.critical(f"PDF generation task FAILED for report_id {report_id}: {e}", exc_info=True)
        # The service method itself handles updating the DB status to 'failed'
    finally:
        db.close()