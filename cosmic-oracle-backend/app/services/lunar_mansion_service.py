# app/services/lunar_mansion_service.py
"""
Lunar Mansions Calculation Service

Calculates the Moon's position within the traditional 28 Lunar Mansions.
"""
import logging
from typing import Dict, Any
from datetime import datetime

from app.services.astrology_service import get_natal_chart_details
from app.services.content_fetch_service import get_lunar_mansions_content

logger = logging.getLogger(__name__)

class LunarMansionService:
    """A singleton service to manage Lunar Mansion data and calculations."""
    _instance = None
    
    def __init__(self):
        logger.info("Initializing LunarMansionService singleton...")
        content = get_lunar_mansions_content()
        self.system_name = content.get("system_name", "Unknown System")
        self.mansions = content.get("mansions", [])
        if not self.mansions:
            raise RuntimeError("Could not load necessary lunar mansions content file.")
        logger.info(f"LunarMansionService initialized with '{self.system_name}' system.")

    def get_current_mansion(self, dt_utc: datetime) -> Dict[str, Any]:
        """
        Calculates the current Lunar Mansion for a given UTC datetime.
        """
        logger.info(f"Calculating lunar mansion for {dt_utc.isoformat()}.")
        try:
            # We only need the Moon's longitude, so a geocentric chart is sufficient and fast.
            chart = get_natal_chart_details(
                datetime_str=dt_utc.isoformat(),
                timezone_str="UTC",
                latitude=0.0,
                longitude=0.0,
                house_system="WholeSign" # Simplest system for this purpose
            )
            if 'error' in chart:
                return {"error": f"Could not calculate Moon's position: {chart['error']}"}

            moon_lon = chart.get('points', {}).get('Moon', {}).get('longitude')
            if moon_lon is None:
                return {"error": "Failed to retrieve Moon's longitude from the chart."}

            # Find the mansion the Moon falls into
            current_mansion = None
            for i, mansion in enumerate(self.mansions):
                start_deg = mansion["start_deg"]
                # The end degree is the start of the next mansion, or 360 for the last one
                end_deg = self.mansions[i + 1]["start_deg"] if i + 1 < len(self.mansions) else 360.0
                
                if start_deg <= moon_lon < end_deg:
                    current_mansion = mansion
                    break
            
            if not current_mansion:
                 # This can happen if moon_lon is exactly 360.0, defaults to the last mansion
                 current_mansion = self.mansions[-1]

            return {
                "calculation_datetime_utc": dt_utc.isoformat(),
                "system_name": self.system_name,
                "moon_longitude": round(moon_lon, 4),
                "current_mansion": current_mansion
            }
        except Exception as e:
            logger.critical(f"An unexpected error occurred in the lunar mansion service: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred."}

# --- Create a single, shared instance ---
try:
    lunar_mansion_service_instance = LunarMansionService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate LunarMansionService: {e}")
    lunar_mansion_service_instance = None