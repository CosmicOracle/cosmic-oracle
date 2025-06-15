# app/services/birth_chart_service.py
"""
Birth Chart Generation and Management Service.
"""
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, time, date

# --- REUSE other services and repositories ---
from app.services.astrology_service import get_natal_chart_details
from app.services.content_fetch_service import get_natal_interpretations
from app.repositories import birth_chart_repository

logger = logging.getLogger(__name__)

class BirthChartService:
    """
    A singleton service that orchestrates birth chart creation, interpretation, and persistence.
    """
    _instance = None
    
    def __init__(self):
        logger.info("Initializing BirthChartService singleton...")
        self.interpretations_content = get_natal_interpretations().get("interpretations", {})
        if not self.interpretations_content:
            raise RuntimeError("Could not load necessary natal interpretations content file.")
        logger.info("BirthChartService initialized successfully.")

    def _generate_interpretations(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """Private helper to generate a full set of interpretations for a calculated chart."""
        interpreted_report = {}
        points = {**chart.get('points', {}), **chart.get('angles', {})}

        for point_name, data in points.items():
            sign = data.get("sign_name")
            house = data.get("house")
            
            # Generate key for sign interpretation, e.g., "sun_in_aries"
            sign_key = f"{point_name.lower().replace(' ', '_')}_in_{sign.lower()}"
            sign_interp = self.interpretations_content.get(sign_key, f"Interpretation for {point_name} in {sign} is not available.")
            
            # Generate key for house interpretation
            house_key = f"{point_name.lower().replace(' ', '_')}_in_house_{house}"
            house_interp = self.interpretations_content.get(house_key, f"Interpretation for {point_name} in House {house} is not available.")
            
            interpreted_report[point_name] = {
                "in_sign": sign_interp,
                "in_house": house_interp
            }
        return interpreted_report

    def create_or_update_user_chart(
        self,
        db: Session,
        user_id: int,
        datetime_str: str,
        timezone_str: str,
        birth_location: str,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Public facade to generate, interpret, and save a birth chart for a user.
        """
        logger.info(f"Generating full birth chart for user {user_id}.")
        try:
            # Step 1: Calculate the full natal chart using the primary astrology service.
            chart_data = get_natal_chart_details(
                datetime_str=datetime_str,
                timezone_str=timezone_str,
                latitude=latitude,
                longitude=longitude,
                house_system="Placidus"
            )
            if 'error' in chart_data:
                return {"error": f"Astrological calculation failed: {chart_data['error']}"}

            # Step 2: Generate all interpretations based on the calculated chart.
            interpretations = self._generate_interpretations(chart_data)

            # Step 3: Persist the raw chart data and interpretations to the database via the repository.
            birth_dt_obj = datetime.fromisoformat(datetime_str)
            
            saved_chart = birth_chart_repository.create_or_update_chart(
                db=db, user_id=user_id,
                birth_date=birth_dt_obj.date(), birth_time=birth_dt_obj.time(),
                birth_location=birth_location, latitude=latitude, longitude=longitude,
                chart_data=chart_data, interpretations=interpretations
            )

            # Step 4: Return a complete response object.
            return {
                "message": "Birth chart processed and saved successfully.",
                "chart_id": saved_chart.id,
                "natal_chart": chart_data,
                "interpretations": interpretations
            }

        except Exception as e:
            logger.critical(f"An unexpected fatal error occurred in the birth chart service for user {user_id}: {e}", exc_info=True)
            db.rollback() # Ensure transaction is rolled back on unexpected failure
            return {"error": "An unexpected internal server error occurred."}

# --- Create a single, shared instance for the application's lifetime ---
try:
    birth_chart_service_instance = BirthChartService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate BirthChartService: {e}")
    birth_chart_service_instance = None