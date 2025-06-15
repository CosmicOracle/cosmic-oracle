# app/services/transit_forecasting_service.py
"""
Transit Forecasting Service

Calculates and interprets significant transit events for a user's natal chart
over a specified period.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

# --- REUSE other services ---
from app.services.astrology_service import get_natal_chart_details
from app.services.aspect_service import aspect_service_instance
from app.services.content_fetch_service import get_transit_interpretations_content

logger = logging.getLogger(__name__)

class TransitForecastingService:
    """A singleton service for generating personalized transit forecasts."""
    _instance = None

    def __init__(self):
        logger.info("Initializing TransitForecastingService singleton...")
        self.interpretations_content = get_transit_interpretations_content().get("interpretations", {})
        if not self.interpretations_content:
            raise RuntimeError("Could not load necessary transit interpretation content.")
        logger.info("TransitForecastingService initialized successfully.")

    def generate_forecast(self, natal_data: Dict[str, Any], start_date_utc: datetime, end_date_utc: datetime) -> Dict[str, Any]:
        """
        Public facade to generate a full transit forecast report.
        """
        logger.info(f"Generating transit forecast for period {start_date_utc.isoformat()} to {end_date_utc.isoformat()}.")
        try:
            # Step 1: Get the user's natal chart points.
            natal_chart = get_natal_chart_details(**natal_data)
            if 'error' in natal_chart:
                return {"error": f"Could not calculate natal chart: {natal_chart['error']}"}
            natal_points = list(natal_chart['points'].values()) + list(natal_chart['angles'].values())

            # Step 2: Iterate through the time period to find transit "hits".
            # A true high-precision engine would solve for exact aspect times.
            # A highly effective and simpler method is to check daily.
            forecast_events = []
            current_date = start_date_utc
            while current_date <= end_date_utc:
                # Get the transiting positions for this day
                transit_chart = get_natal_chart_details(
                    datetime_str=current_date.isoformat(),
                    timezone_str="UTC", latitude=0, longitude=0, house_system="Placidus"
                )
                if 'error' in transit_chart: continue
                
                transiting_points = list(transit_chart['points'].values())

                # Step 3: Check aspects between each transiting planet and each natal point.
                for t_point in transiting_points:
                    # We only care about major transiting bodies for forecasts
                    if t_point['name'] not in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
                        continue
                    
                    # Use the centralized aspect service to check for aspects
                    aspects = aspect_service_instance.find_all_aspects([t_point] + natal_points)
                    
                    for aspect in aspects:
                        # We only want aspects from the transiting planet to a natal point, with a tight orb
                        if aspect['point1_name'] == t_point['name'] and aspect['orb_degrees'] <= 1.5:
                            natal_point_name = aspect['point2_name']
                            aspect_name = aspect['aspect_name'].lower()
                            
                            # Create a key to look up the interpretation
                            key = f"transiting_{t_point['name'].lower()}_{aspect_name}_natal_{natal_point_name.lower().replace(' ', '_')}"
                            interpretation = self.interpretations_content.get(key, {})

                            forecast_events.append({
                                "date": current_date.strftime('%Y-%m-%d'),
                                "title": interpretation.get("title", f"Transiting {t_point['name']} {aspect_name.title()} Natal {natal_point_name}"),
                                "impact": interpretation.get("impact", "low"),
                                "theme": interpretation.get("theme", "General"),
                                "opportunity": interpretation.get("opportunity", "N/A"),
                                "challenge": interpretation.get("challenge", "N/A"),
                                "orb_degrees": aspect['orb_degrees']
                            })
                
                current_date += timedelta(days=1)
            
            # Remove duplicate events for the same transit that might appear on consecutive days
            unique_events = {event['title']: event for event in forecast_events}.values()

            return {"forecast_events": sorted(list(unique_events), key=lambda x: x['date'])}

        except Exception as e:
            logger.critical(f"An unexpected fatal error in the transit forecast service: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred during forecast generation."}

# --- Create a single, shared instance ---
try:
    transit_forecasting_service_instance = TransitForecastingService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate TransitForecastingService: {e}")
    transit_forecasting_service_instance = None