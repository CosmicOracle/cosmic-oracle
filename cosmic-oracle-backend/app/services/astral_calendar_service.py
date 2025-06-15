# app/services/astral_calendar_service.py
"""
Astral Calendar Service

This service calculates major astronomical and astrological events for a given
time period, such as moon phases, eclipses, and planetary retrogrades.
"""
import logging
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List

# Third-party library imports
from skyfield.api import load, wgs84
from skyfield.framelib import ecliptic_frame
from skyfield.almanac import find_discrete, risings_and_settings, phases, eclipses

# Local application imports
from app.core.config import settings
from app.services.content_fetch_service import get_astral_events_content
from app.repositories import calendar_repository
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class AstralCalendarService:
    """
    A singleton service that provides all astronomical event calculations.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AstralCalendarService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized: return
        logger.info("Initializing AstralCalendarService singleton...")
        self.ts = load.timescale()
        self.eph = load(settings.skyfield_ephemeris)
        self.interpretations = get_astral_events_content().get("event_interpretations", {})
        self._initialized = True
        logger.info("AstralCalendarService initialized successfully.")

    def _get_moon_phases(self, start_t, end_t) -> List[Dict[str, Any]]:
        """Calculates New, First Quarter, Full, and Last Quarter moons."""
        t, y = phases(self.eph, start_t, end_t)
        phase_names = {0: 'New Moon', 1: 'First Quarter', 2: 'Full Moon', 3: 'Last Quarter'}
        return [{
            "title": phase_names[yi],
            "event_type": "moon_phase",
            "start_date": ti.utc_iso(),
            "description": f"The {phase_names[yi]} marks a key point in the lunar cycle."
        } for ti, yi in zip(t, y)]

    def _get_eclipses(self, start_t, end_t) -> List[Dict[str, Any]]:
        """Calculates all solar and lunar eclipses in the time frame."""
        t, y, _, _ = eclipses(self.eph, start_t, end_t)
        eclipse_types = {0: "Total Solar", 1: "Annular Solar", 2: "Partial Solar", 3: "Penumbral Lunar", 4: "Partial Lunar", 5: "Total Lunar"}
        events = []
        for ti, yi in zip(t, y):
            eclipse_type = eclipse_types.get(yi, "Eclipse")
            interp_key = "solar_eclipse" if "Solar" in eclipse_type else "lunar_eclipse"
            interpretation = self.interpretations.get(interp_key, {})
            events.append({
                "title": f"{eclipse_type} Eclipse",
                "event_type": interp_key,
                "start_date": ti.utc_iso(),
                "description": interpretation.get("summary", f"A significant {eclipse_type} Eclipse occurs."),
                "keywords": interpretation.get("keywords", [])
            })
        return events

    def _get_retrogrades(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Finds the start and end of retrograde periods for major planets."""
        # This is computationally intensive; a real-world app might pre-calculate this
        # and store it in a database. But here is a real, on-the-fly calculation.
        events = []
        planets = ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        start_t, end_t = self.ts.from_datetime(start_date), self.ts.from_datetime(end_date)
        
        for planet_name in planets:
            planet = self.eph[planet_name]
            
            # Find times when apparent motion is zero (the stations)
            t, y, _, _ = find_discrete(start_t, end_t, self.eph.apparent_speed_in_right_ascension(planet))
            
            for ti, yi in zip(t, y):
                # yi is True if motion is switching from prograde to retrograde
                event_type = "retrograde_start" if yi else "retrograde_end"
                interp_key = f"{planet_name}_retrograde"
                interpretation = self.interpretations.get(interp_key, {})
                events.append({
                    "title": f"{planet_name.capitalize()} stations {'retrograde' if yi else 'direct'}",
                    "event_type": event_type,
                    "start_date": ti.utc_iso(),
                    "description": interpretation.get("summary", f"{planet_name.capitalize()} begins its {'retrograde' if yi else 'direct'} phase."),
                    "keywords": interpretation.get("keywords", [])
                })
        return events

    def get_all_cosmic_events(self, start_date_str: str, end_date_str: str) -> Dict[str, Any]:
        """Public method to get all calculated astronomical events."""
        try:
            start_dt = datetime.fromisoformat(start_date_str).replace(tzinfo=pytz.utc)
            end_dt = datetime.fromisoformat(end_date_str).replace(tzinfo=pytz.utc)
            
            start_t = self.ts.from_datetime(start_dt)
            end_t = self.ts.from_datetime(end_dt)
            
            all_events = []
            all_events.extend(self._get_moon_phases(start_t, end_t))
            all_events.extend(self._get_eclipses(start_t, end_t))
            all_events.extend(self._get_retrogrades(start_dt, end_dt))
            
            all_events.sort(key=lambda x: x['start_date'])
            return {"events": all_events}
        except Exception as e:
            logger.error(f"Error calculating cosmic events: {e}", exc_info=True)
            return {"error": "Failed to calculate cosmic events."}
    
    def get_combined_calendar_for_user(self, db: Session, user_id: int, start_date_str: str, end_date_str: str) -> Dict[str, Any]:
        """Combines cosmic events with a user's personal events from the database."""
        cosmic_events_result = self.get_all_cosmic_events(start_date_str, end_date_str)
        if "error" in cosmic_events_result:
            return cosmic_events_result

        all_events = cosmic_events_result.get("events", [])

        start_dt = datetime.fromisoformat(start_date_str).replace(tzinfo=pytz.utc)
        end_dt = datetime.fromisoformat(end_date_str).replace(tzinfo=pytz.utc)
        
        personal_events = calendar_repository.get_personal_events_for_user(db, user_id, start_dt, end_dt)
        for event in personal_events:
            all_events.append({
                "title": event.title,
                "event_type": "personal_event",
                "start_date": event.event_date.isoformat(),
                "description": event.description
            })

        all_events.sort(key=lambda x: x['start_date'])
        return {"events": all_events}

# --- Create a single, shared instance for the application's lifetime ---
try:
    calendar_service_instance = AstralCalendarService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate AstralCalendarService: {e}")
    calendar_service_instance = None