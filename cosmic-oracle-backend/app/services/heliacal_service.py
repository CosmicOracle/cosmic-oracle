# app/services/heliacal_service.py
"""
Heliacal Events Service

Calculates the heliacal rising and setting of planets and major fixed stars,
a key technique in traditional and ancient astrology.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from skyfield.api import Star, load, wgs84
from skyfield.almanac import find_discrete

from app.core.config import settings
from app.services.content_fetch_service import get_heliacal_content

logger = logging.getLogger(__name__)

# Standard astronomical definitions for visibility
# Arc of Vision (AV): Altitude difference between Sun and star required for visibility.
# A standard value for a first-magnitude star like Regulus is ~11 degrees.
# Sun must be this far *below* the horizon when the star is *on* the horizon.
ARC_OF_VISION = 11.0 

class HeliacalService:
    """
    A singleton service that manages Skyfield resources and provides
    heliacal event calculations.
    """
    _instance = None

    def __init__(self):
        logger.info("Initializing HeliacalService singleton...")
        self.ts = load.timescale()
        self.eph = load(settings.skyfield_ephemeris)
        self.earth = self.eph['earth']
        self.sun = self.eph['sun']
        
        content = get_heliacal_content()
        self.interpretations = content.get("event_interpretations", {})
        self.star_interpretations = content.get("major_stars", {})
        
        # Skyfield's Star object requires RA, Dec, and other data for a specific epoch (J2000.0)
        self.fixed_stars = {
            'Sirius': Star.from_name('Sirius'),
            'Regulus': Star.from_name('Regulus'),
            'Aldebaran': Star.from_name('Aldebaran'),
            'Antares': Star.from_name('Antares'),
            'Spica': Star.from_name('Spica')
        }
        logger.info("HeliacalService initialized successfully with star catalog.")

    def _get_skyfield_body(self, name: str) -> Optional[Any]:
        """Gets the Skyfield object for a planet or a pre-defined fixed star."""
        if name in self.fixed_stars:
            return self.fixed_stars[name]
        if name.lower() in self.eph.names():
            return self.eph[name.lower()]
        return None

    def find_heliacal_events(self, start_date: datetime, end_date: datetime, latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """
        Finds all major heliacal events for pre-defined bodies in a time range.
        """
        observer = self.earth + wgs84.latlon(latitude, longitude)
        start_t = self.ts.from_datetime(start_date)
        end_t = self.ts.from_datetime(end_date)
        
        all_events = []

        for name, body in self.fixed_stars.items(): # Could expand to planets too
            
            # --- Define the search function for Skyfield's almanac ---
            # We are looking for the moment when the Sun is at a specific altitude
            # *below* the horizon. The function will be zero at this moment.
            def heliacal_event_function(t):
                # We need the altitude of the star and the sun at time `t`
                star_alt, _, _ = observer.at(t).observe(body).apparent().altaz()
                sun_alt, _, _ = observer.at(t).observe(self.sun).apparent().altaz()
                
                # Heliacal condition: Star is on the horizon (alt=0) AND Sun is at a specific depth.
                # We can combine this: Is the star's altitude + the Sun's required depth equal to zero?
                # The function returns the difference from the ideal condition.
                return star_alt.degrees - (sun_alt.degrees + ARC_OF_VISION)

            # Set the step size for the search
            heliacal_event_function.step_days = 1.0
            
            times, events = find_discrete(start_t, end_t, heliacal_event_function)
            
            # `events` will be True for a rising (morning), False for a setting (evening)
            for t_event, is_rising in zip(times, events):
                event_type = "heliacal_rising" if is_rising else "heliacal_setting"
                interp = self.interpretations.get(event_type, {})
                
                all_events.append({
                    "event_name": f"{name} {interp.get('title', event_type.replace('_', ' ').title())}",
                    "event_type": event_type,
                    "datetime_utc": t_event.utc_iso(),
                    "body_name": name,
                    "summary": self.star_interpretations.get(name, ""),
                    "influence": interp.get("summary", "")
                })

        all_events.sort(key=lambda x: x['datetime_utc'])
        return all_events


# --- Create a single, shared instance for the application's lifetime ---
try:
    heliacal_service_instance = HeliacalService()
except Exception as e:
    logger.critical(f"Could not instantiate HeliacalService: {e}", exc_info=True)
    heliacal_service_instance = None