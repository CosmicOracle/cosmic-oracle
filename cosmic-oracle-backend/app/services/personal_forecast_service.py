# app/services/personal_forecast_service.py
"""
Personalized Forecast and 'Personal Sky' Service

Orchestrates multiple astrological services to generate a personalized forecast
for a user by comparing their natal chart to current cosmic events.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

# --- REUSE our existing, powerful services ---
from app.services.astrology_service import get_natal_chart_details
from app.services.predictive_service import analyze_transits # The real transit calculator
from app.services.content_fetch_service import get_personal_forecast_content
from app.repositories import birth_chart_repository # For fetching user chart data
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class PersonalForecastService:
    """
    A singleton service that generates personalized daily insights for users.
    """
    _instance = None
    
    def __init__(self):
        logger.info("Initializing PersonalForecastService singleton...")
        content = get_personal_forecast_content()
        self.interpretations = content.get("aspect_interpretations", {})
        if not self.interpretations:
            raise RuntimeError("Could not load personal forecast interpretation content.")
        logger.info("PersonalForecastService initialized successfully.")

    def get_personal_sky_for_today(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Generates a 'Personal Sky' report for the current moment, combining a user's
        natal data with live transits.
        """
        logger.info(f"Generating personal sky for user {user_id}.")
        try:
            # Step 1: Get the user's saved birth chart from the database via the repository.
            birth_chart_record = birth_chart_repository.find_by_user_id(db, user_id)
            if not birth_chart_record:
                return {"error": "No birth chart found for this user. Please create one first."}

            # Step 2: Use the saved data to call the transit analysis service.
            # We are calculating transits for "now" at the user's birth location.
            now = datetime.now(timezone.utc)
            natal_data = {
                "datetime_str": birth_chart_record.birth_datetime.isoformat(),
                "timezone_str": birth_chart_record.timezone,
                "latitude": birth_chart_record.latitude,
                "longitude": birth_chart_record.longitude,
                "house_system": "Placidus"
            }
            transit_result = analyze_transits(
                natal_chart_data=natal_data,
                transit_datetime_str=now.isoformat(),
                timezone_str="UTC",
                latitude=birth_chart_record.latitude,
                longitude=birth_chart_record.longitude
            )
            if 'error' in transit_result:
                return {"error": f"Failed to calculate current transits: {transit_result['error']}"}

            # Step 3: Add personalized interpretations to the most significant transits.
            significant_transits = []
            for aspect in transit_result.get("predictive_analysis", {}).get("active_transit_aspects", []):
                # Create a key to look up in our content file
                key = f"transiting_{aspect['transiting_planet'].lower()}_{aspect['aspect_name'].lower()}_natal_{aspect['natal_point'].lower()}"
                interpretation = self.interpretations.get(key, {
                    "title": "General Influence",
                    "impact": "low",
                    "areas": ["general"],
                    "advice": "A background cosmic energy is present. Be mindful of its themes."
                })
                aspect_with_interp = {**aspect, "interpretation": interpretation}
                significant_transits.append(aspect_with_interp)

            return {
                "personal_sky_report": {
                    "user_id": user_id,
                    "generated_at_utc": now.isoformat(),
                    "significant_transits_now": significant_transits
                }
            }
            
        except Exception as e:
            logger.critical(f"An unexpected error occurred generating personal sky for user {user_id}: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred."}

# --- Create a single, shared instance ---
try:
    personal_forecast_service_instance = PersonalForecastService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate PersonalForecastService: {e}")
    personal_forecast_service_instance = None