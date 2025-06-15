# app/services/planetary_hours_service.py
"""
Planetary Hours Calculation Service
"""
import logging
from datetime import datetime, time, timedelta, timezone
from typing import Dict, Any, List

from skyfield.almanac import sunrise_sunset
from app.services.moon_service import moon_service_instance # Reusing its skyfield instance
from app.services.content_fetch_service import get_planetary_hours_content

logger = logging.getLogger(__name__)

class PlanetaryHoursService:
    """A singleton service for calculating planetary hours."""
    _instance = None

    def __init__(self):
        logger.info("Initializing PlanetaryHoursService singleton...")
        self.interpretations = get_planetary_hours_content().get("hour_interpretations", {})
        self.chaldean_order = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        self.day_rulers = {6: "Sun", 0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter", 4: "Venus", 5: "Saturn"} # Monday=0
        if not self.interpretations:
            raise RuntimeError("Could not load planetary hours content.")
        logger.info("PlanetaryHoursService initialized successfully.")

    def calculate_hours_for_day(self, target_date: date, latitude: float, longitude: float) -> Dict[str, Any]:
        """Calculates the full 24 planetary hours for a given date and location."""
        try:
            observer = moon_service_instance.eph['earth'] + moon_service_instance.wgs84.latlon(latitude, longitude)
            ts = moon_service_instance.ts
            
            # Create a 48-hour window around the target date to find all relevant sunrises/sunsets
            start_t = ts.from_datetime(datetime.combine(target_date, time.min, tzinfo=timezone.utc) - timedelta(days=1))
            end_t = ts.from_datetime(datetime.combine(target_date, time.max, tzinfo=timezone.utc) + timedelta(days=1))
            
            t, y = sunrise_sunset(moon_service_instance.eph, observer, start_t, end_t)
            
            # Find the sunrise that starts the desired day
            today_sunrise = None
            for ti, yi in zip(t, y):
                if yi and ti.to_datetime().date() == target_date:
                    today_sunrise = ti.to_datetime()
                    break
            if not today_sunrise: return {"error": "Could not determine sunrise for the target date."}
            
            # Find the subsequent sunset and the next day's sunrise
            today_sunset = next((ti.to_datetime() for ti, yi in zip(t, y) if not yi and ti.to_datetime() > today_sunrise), None)
            next_sunrise = next((ti.to_datetime() for ti, yi in zip(t, y) if yi and ti.to_datetime() > today_sunset), None)
            
            if not today_sunset or not next_sunrise: return {"error": "Could not determine the full day/night cycle."}
            
            # Calculate durations
            day_hour_duration = (today_sunset - today_sunrise) / 12
            night_hour_duration = (next_sunrise - today_sunset) / 12
            
            day_ruler = self.day_rulers[today_sunrise.weekday()]
            first_hour_ruler_index = self.chaldean_order.index(day_ruler)
            
            all_hours = []
            # Day Hours
            for i in range(12):
                ruler = self.chaldean_order[(first_hour_ruler_index + i) % 7]
                all_hours.append({
                    "hour_number": i + 1, "type": "Day", "ruler": ruler,
                    "start_time_utc": (today_sunrise + i * day_hour_duration).isoformat(),
                    "end_time_utc": (today_sunrise + (i + 1) * day_hour_duration).isoformat(),
                    "interpretation": self.interpretations.get(ruler)
                })
            # Night Hours
            for i in range(12):
                ruler = self.chaldean_order[(first_hour_ruler_index + 12 + i) % 7]
                all_hours.append({
                    "hour_number": i + 1, "type": "Night", "ruler": ruler,
                    "start_time_utc": (today_sunset + i * night_hour_duration).isoformat(),
                    "end_time_utc": (today_sunset + (i + 1) * night_hour_duration).isoformat(),
                    "interpretation": self.interpretations.get(ruler)
                })
            
            return {"planetary_hours_schedule": all_hours}
            
        except Exception as e:
            logger.error(f"Error calculating planetary hours: {e}", exc_info=True)
            return {"error": "An internal error occurred during calculation."}

try:
    planetary_hours_service_instance = PlanetaryHoursService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate PlanetaryHoursService: {e}")
    planetary_hours_service_instance = None