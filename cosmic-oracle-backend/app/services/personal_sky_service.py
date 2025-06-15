# app/services/personal_sky_service.py
"""
High-Level Orchestrator for the 'Personal Sky' Dashboard.

This service gathers data from all other relevant services (natal, predictive,
moon, planetary hours, etc.) to build a complete data object for the user's
personalized dashboard.
"""
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone, time

# --- REUSE our existing, powerful services ---
from app.repositories import birth_chart_repository
from app.services.predictive_service import transit_forecasting_service_instance
from app.services.moon_service import moon_service_instance
from app.services.planetary_hours_service import planetary_hours_service_instance
from app.services.ai_synthesis_service import ai_synthesis_service_instance

logger = logging.getLogger(__name__)

class PersonalSkyService:
    """A singleton service to orchestrate the generation of the Personal Sky dashboard."""
    _instance = None

    def __init__(self):
        logger.info("Initializing PersonalSkyService singleton...")
        if not all([transit_forecasting_service_instance, moon_service_instance, planetary_hours_service_instance, ai_synthesis_service_instance]):
            raise RuntimeError("One or more required services for PersonalSkyService are not available.")
        logger.info("PersonalSkyService initialized successfully.")

    def get_dashboard_data(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        The main public method. Gathers all data for the dashboard.
        """
        logger.info(f"Generating Personal Sky Dashboard for user {user_id}.")
        try:
            # 1. Get the user's saved birth chart.
            birth_chart_record = birth_chart_repository.find_by_user_id(db, user_id)
            if not birth_chart_record:
                return {"error": "No birth chart found for this user. Please create one first."}

            natal_data = {
                "datetime_str": birth_chart_record.birth_datetime.isoformat(),
                "timezone_str": birth_chart_record.timezone,
                "latitude": birth_chart_record.latitude,
                "longitude": birth_chart_record.longitude,
                "house_system": "Placidus",
                "full_name": birth_chart_record.user.full_name # Assuming relationship is loaded
            }
            
            now_utc = datetime.now(timezone.utc)
            today_date = now_utc.date()

            # 2. Call all other services to gather data points.
            # Get today's transits
            transit_result = transit_forecasting_service_instance.generate_forecast(natal_data, now_utc, now_utc)
            
            # Get current moon phase and which natal house it's in
            moon_details = moon_service_instance.get_moon_details(now_utc)
            # This requires a natal chart calculation to find the house
            from app.services.astrology_service import get_natal_chart_details
            temp_chart = get_natal_chart_details(**natal_data)
            moon_details['house'] = temp_chart.get('points', {}).get('Moon', {}).get('house')
            
            # Get planetary hours for today
            hours_schedule = planetary_hours_service_instance.calculate_hours_for_day(today_date, natal_data['latitude'], natal_data['longitude'])
            
            # Find the current and next planetary hour
            current_hour = next((h for h in hours_schedule.get('planetary_hours_schedule', []) if datetime.fromisoformat(h['start_time_utc']) <= now_utc < datetime.fromisoformat(h['end_time_utc'])), None)
            next_hour = next((h for h in hours_schedule.get('planetary_hours_schedule', []) if datetime.fromisoformat(h['start_time_utc']) > now_utc), None)

            # 3. Assemble the complete data object.
            dashboard_payload = {
                "generated_at_utc": now_utc.isoformat(),
                "most_important_transit": transit_result.get('forecast_events', [None])[0],
                "transiting_moon_info": moon_details,
                "current_planetary_hour": current_hour,
                "next_planetary_hour": next_hour,
            }

            # 4. Pass the data to the AI service for a synthesized summary.
            dashboard_payload['synthesized_forecast'] = ai_synthesis_service_instance.synthesize_daily_forecast(dashboard_payload)

            return {"personal_sky_dashboard": dashboard_payload}

        except Exception as e:
            logger.critical(f"An unexpected error occurred generating dashboard for user {user_id}: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred."}

# --- Create a single, shared instance ---
try:
    personal_sky_service_instance = PersonalSkyService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate PersonalSkyService: {e}")
    personal_sky_service_instance = None