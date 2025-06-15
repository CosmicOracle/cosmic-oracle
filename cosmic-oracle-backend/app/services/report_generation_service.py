# app/services/report_generation_service.py
"""
Service for orchestrating the generation of complex PDF reports.
"""
import logging
import os
from typing import Dict, Any

from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.repositories import report_repository
from app.services import astrology_service, numerology_service, compatibility_service
from app.tasks.report_tasks import generate_full_report_pdf # Import the background task
from app.core.config import settings

logger = logging.getLogger(__name__)

class ReportGenerationService:
    """Orchestrates data gathering and PDF creation for various reports."""
    
    def request_natal_report(self, db: Session, user_id: int, natal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a pending report record and queues the PDF generation task."""
        logger.info(f"Requesting new Natal Report for user {user_id}.")
        report_record = report_repository.create_pending_report(db, user_id, 'natal', natal_data)
        
        # Trigger the background task
        generate_full_report_pdf.delay(report_record.id)
        
        return {"message": "Your Natal Report is being generated.", "report_id": report_record.id, "status": "pending"}

    def generate_and_save_pdf(self, db: Session, report_id: int):
        """
        The core worker method called by the background task.
        Gathers all data and builds the PDF.
        """
        report = report_repository.find_report_by_id(db, report_id) # No user_id needed for internal task
        if not report or report.status != 'pending':
            logger.warning(f"Report {report_id} not found or not in pending state. Aborting task.")
            return

        try:
            # Step 1: Gather all the necessary data based on report type
            if report.report_type == 'natal':
                report_content = self._gather_natal_report_data(report.input_data)
            else:
                raise ValueError(f"Unknown report type: {report.report_type}")

            # Step 2: Build the PDF
            file_identifier = self._build_pdf(report.id, report.report_type, report_content)

            # Step 3: Update the report record to 'completed'
            report_repository.update_report_status_to_completed(db, report.id, file_identifier)
        
        except Exception as e:
            logger.error(f"Error generating PDF for report {report.id}: {e}", exc_info=True)
            report_repository.update_report_status_to_failed(db, report.id, str(e))

    def _gather_natal_report_data(self, input_data: Dict) -> Dict:
        """Fetches all data required for a natal report from various services."""
        chart_data = astrology_service.get_natal_chart_details(**input_data)
        # Add other service calls here as needed (e.g., numerology)
        return {"chart": chart_data}

    def _build_pdf(self, report_id: int, report_type: str, content: Dict) -> str:
        """Constructs a PDF file from the report content using reportlab."""
        # Ensure the reports directory exists
        reports_dir = settings.REPORTS_STORAGE_PATH # Assumes this is in your config
        os.makedirs(reports_dir, exist_ok=True)

        file_name = f"{report_type}_report_{report_id}.pdf"
        file_path = os.path.join(reports_dir, file_name)

        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # --- Build the PDF content ---
        story.append(Paragraph("Cosmic Oracle Natal Report", styles['h1']))
        story.append(Spacer(1, 24))
        
        # Add Sun Sign info
        sun_data = content.get('chart', {}).get('points', {}).get('Sun', {})
        if sun_data:
            story.append(Paragraph(f"Sun in {sun_data.get('sign_name')}", styles['h2']))
            story.append(Paragraph("Your core identity, ego, and life force are expressed through the lens of this sign...", styles['Normal']))
            story.append(Spacer(1, 12))

        # Add more sections for Moon, Ascendant, etc.
        # This is where you would loop through all the content and format it.

        doc.build(story)
        logger.info(f"Successfully built PDF for report {report_id} at {file_path}")
        return file_path

# --- Create a single, shared instance ---
report_generation_service_instance = ReportGenerationService()