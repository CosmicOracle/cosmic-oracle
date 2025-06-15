# app/services/house_calculator_service.py
"""
Dedicated House Calculation Service

This service provides a clean interface for calculating astrological house cusps
using various house systems supported by Swiss Ephemeris.
"""
import logging
from datetime import datetime
from typing import Dict, List, Any
import swisseph as swe

from app.core.config import settings # To ensure ephemeris path is set

logger = logging.getLogger(__name__)

class HouseCalculatorService:
    """
    A utility class for calculating house cusps. This service is stateless
    and can be instantiated as needed, or used as a singleton.
    """
    # Map user-friendly names to swisseph's single-character byte codes
    HOUSE_SYSTEMS_MAP: Dict[str, bytes] = {
        'placidus': b'P', 'koch': b'K', 'porphyry': b'O',
        'regiomontanus': b'R', 'campanus': b'C', 'equal': b'E',
        'whole_sign': b'W', 'axial_rotation': b'X', 'morinus': b'M',
        'alcabitus': b'B'
    }

    def __init__(self):
        # The main astrology service already sets this, but this is a safeguard.
        swe.set_ephe_path(settings.sweph_path)
        logger.info("HouseCalculatorService initialized.")

    def calculate_cusps(
        self,
        dt_utc: datetime,
        latitude: float,
        longitude: float,
        house_system_key: str
    ) -> Dict[str, Any]:
        """
        Calculates the 12 house cusps and major angles for a given time and location.
        """
        system_code = self.HOUSE_SYSTEMS_MAP.get(house_system_key.lower())
        if not system_code:
            return {"error": f"Invalid house system '{house_system_key}'. Supported systems: {list(self.HOUSE_SYSTEMS_MAP.keys())}"}

        try:
            # Convert python datetime to Julian Day for Swisseph
            jd_utc = swe.utc_to_jd(
                dt_utc.year, dt_utc.month, dt_utc.day,
                dt_utc.hour, dt_utc.minute, dt_utc.second,
                1 # Gregorian calendar
            )[1]
            
            # The core swisseph calculation
            cusps, ascmc = swe.houses(jd_utc, latitude, longitude, system_code)
            
            # Format the output clearly
            return {
                "calculation_input": {
                    "datetime_utc": dt_utc.isoformat(),
                    "latitude": latitude,
                    "longitude": longitude,
                    "house_system": house_system_key
                },
                "results": {
                    "house_cusps": {i + 1: round(cusps[i], 4) for i in range(12)},
                    "angles": {
                        "ascendant": round(ascmc[0], 4),
                        "midheaven_mc": round(ascmc[1], 4),
                        "vertex": round(ascmc[3], 4)
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error calculating houses: {e}", exc_info=True)
            return {"error": f"An internal Swiss Ephemeris error occurred: {str(e)}"}

# --- Create a single, shared instance for the application's lifetime ---
house_calculator_instance = HouseCalculatorService()