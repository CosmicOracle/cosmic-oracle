# app/services/year_ahead_report_service.py
"""
Service for orchestrating the generation of Year Ahead astrological reports.
"""
import logging
import os
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

# PDF Generation Library
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# --- REUSE our existing, powerful services and repositories ---
from app.repositories import report_repository
from app.services import predictive_service, solar_return_service, numerology_service
from app.services.content_fetch_service import get_year_ahead_report_content
from app.tasks.report_tasks import generate_year_ahead_pdf # The background task
from app.core.config import settings

logger = logging.getLogger(__name__)

class YearAheadReportService:
    """Orchestrates data gathering and PDF creation for Year Ahead reports."""
    
    def __init__(self):
        self.content = get_year_ahead_report_content()
        self.styles = getSampleStyleSheet()

    def request_report(self, db: Session, user_id: int, natal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a pending report record and queues the PDF generation task."""
        logger.info(f"Requesting new Year Ahead Report for user {user_id}.")
        report_record = report_repository.create_pending_report(db, user_id, 'year_ahead', natal_data)
        generate_year_ahead_pdf.delay(report_record.id)
        return {"message": "Your Year Ahead Report is being generated.", "report_id": report_record.id, "status": "pending"}

    def generate_and_save_pdf(self, db: Session, report_id: int):
        """The core worker method called by the background task."""
        report = report_repository.find_report_by_id(db, report_id)
        if not report or report.status != 'pending': return

        try:
            report_content = self._gather_report_data(report.input_data)
            file_identifier = self._build_pdf(report.id, report_content)
            report_repository.update_report_as_completed(db, report.id, file_identifier)
        except Exception as e:
            logger.error(f"Error generating PDF for report {report.id}: {e}", exc_info=True)
            report_repository.update_report_as_failed(db, report.id, str(e))

    def _gather_report_data(self, natal_data: Dict) -> Dict:
        """Fetches all data required for a year-ahead report from various services."""
        now = datetime.now(timezone.utc)
        start_date = now
        end_date = now + timedelta(days=365)
        target_year = now.year

        # Fetch data from all relevant services
        solar_return_chart = solar_return_service.calculate_solar_return_chart(natal_data, target_year, natal_data['latitude'], natal_data['longitude'])
        progressions = predictive_service.analyze_secondary_progressions(natal_data, target_age=(target_year - datetime.fromisoformat(natal_data['datetime_str']).year))
        transits = predictive_service.analyze_transits(natal_data, start_date.isoformat(), end_date.isoformat(), 'UTC', natal_data['latitude'], natal_data['longitude'])
        numerology = numerology_service.numerology_service_instance.generate_report_numbers(natal_data['full_name'], datetime.fromisoformat(natal_data['datetime_str']).date()) # Requires a name field in natal_data
        
        return {
            "start_date": start_date.strftime('%B %d, %Y'), "end_date": end_date.strftime('%B %d, %Y'),
            "solar_return": solar_return_chart,
            "progressions": progressions,
            "transits": transits,
            "numerology": numerology
        }

    def _build_pdf(self, report_id: int, content: Dict) -> str:
        """Constructs a professional PDF file from the report content."""
        reports_dir = settings.REPORTS_STORAGE_PATH
        os.makedirs(reports_dir, exist_ok=True)
        file_path = os.path.join(reports_dir, f"year_ahead_report_{report_id}.pdf")
        
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        # --- Build PDF Document ---
        story.append(Paragraph(self.content['title_template'].format(start_date=content['start_date'], end_date=content['end_date']), self.styles['h1']))
        story.append(Paragraph(self.content['introduction'], self.styles['Normal']))
        story.append(Spacer(1, 24))

        # Numerology Section
        story.append(Paragraph(self.content['sections']['personal_year']['title'], self.styles['h2']))
        story.append(Paragraph(self.content['sections']['personal_year']['description'], self.styles['Italic']))
        pn_year = str(content['numerology']['personal_year_number'])
        story.append(Paragraph(f"<b>Your Personal Year is {pn_year}:</b> {self.content['numerology_interpretations'].get(pn_year, '')}", self.styles['Normal']))
        story.append(PageBreak())
        
        # Solar Return Section
        story.append(Paragraph(self.content['sections']['solar_return']['title'], self.styles['h2']))
        story.append(Paragraph(self.content['sections']['solar_return']['description'], self.styles['Italic']))
        sr_chart = content['solar_return'].get('solar_return_chart', {})
        if 'error' not in sr_chart:
            sr_asc = sr_chart.get('angles', {}).get('Ascendant', {})
            sr_sun = sr_chart.get('points', {}).get('Sun', {})
            story.append(Paragraph(f"<b>Solar Return Ascendant:</b> {sr_asc.get('sign_name')}. This sets the primary focus and approach for your year.", self.styles['Normal']))
            story.append(Paragraph(f"<b>Solar Return Sun in House {sr_sun.get('house')}:</b> This highlights the area of life where you are meant to shine and express your vitality.", self.styles['Normal']))
        story.append(PageBreak())

        # Transits Section
        story.append(Paragraph(self.content['sections']['transits']['title'], self.styles['h2']))
        story.append(Paragraph(self.content['sections']['transits']['description'], self.styles['Italic']))
        for transit in content.get('transits', {}).get('predictive_analysis', {}).get('active_transit_aspects', [])[:5]: # Top 5
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"<b>{transit['transiting_planet']} {transit['aspect_name']} your Natal {transit['natal_point']}</b>", self.styles['h3']))
            # Here you would fetch interpretation from another content file
            story.append(Paragraph("This transit brings themes of...", self.styles['Normal']))

        doc.build(story)
        logger.info(f"Successfully built PDF for report {report_id} at {file_path}")
        return file_path

# --- Create a single, shared instance ---
report_generation_service_instance = ReportGenerationService()