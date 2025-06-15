# app/services/horoscope_service.py
"""
Dynamic Horoscope Generation Service

This service generates astrologically-grounded horoscopes on the fly by
calculating real-time transits to a representative Sun position for each
zodiac sign.
"""
import logging
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional

# IMPORTANT: Do NOT import 'astrology_service' directly from 'app' here.
# It will be passed into this service's constructor.
# REMOVED: from app.services.astrology_service import get_natal_chart_details # <-- THIS LINE IS THE PROBLEM
# Import the ContentFetchService CLASS for type hinting and potential direct use
from app.services.content_fetch_service import ContentFetchService
# Assuming AstrologyService is imported for type hints in __init__
from app.services.astrology_service import AstrologyService


logger = logging.getLogger(__name__)

# --- Production-Grade Logging Setup ---
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class HoroscopeService:
    _instance = None # For optional singleton pattern

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(HoroscopeService, cls).__new__(cls)
        return cls._instance

    # COMBINED AND CORRECTED __init__
    def __init__(self, astrology_service_instance: AstrologyService = None, content_fetch_service_instance: ContentFetchService = None):
        # Prevent re-initialization if already initialized via __new__
        if hasattr(self, '_initialized') and self._initialized:
            return

        logger.info("Initializing HoroscopeService...")
        
        # IMPORTANT: Receive service instances via constructor
        if astrology_service_instance is None:
            raise RuntimeError("AstrologyService instance must be provided to HoroscopeService.")
        self.astrology_service = astrology_service_instance

        if content_fetch_service_instance is None:
            raise RuntimeError("ContentFetchService instance must be provided to HoroscopeService.")
        self.content_fetch_service = content_fetch_service_instance

        # Load content data using the passed content_fetch_service instance
        # Ensure content_fetch_service methods exist and return dicts/expected types
        self.general_themes = self.content_fetch_service.get_horoscope_interpretations_data().get("general_themes", {})
        self.aspect_interpretations = self.content_fetch_service.get_horoscope_interpretations_data().get("aspect_interpretations", {})
        
        self.zodiac_data = self.content_fetch_service.get_zodiac_signs_data() 
        self.planetary_base_data = self.content_fetch_service.get_planetary_base_data() 
        self.aspect_base_data = self.content_fetch_service.get_aspect_base_data() 
        
        # Robustness check for loaded data
        if not all([self.general_themes, self.aspect_interpretations, self.zodiac_data]):
            logger.critical("Missing essential horoscope or zodiac content. Please check JSON files.")
            raise RuntimeError("Could not load necessary horoscope or zodiac content files from content_fetch_service.")
        
        # Assuming zodiac_data keys are correct for direct access like 'aries', 'taurus'
        if self.zodiac_data:
            self.sign_longitudes = {
                sign_key: (i * 30 + 15) for i, sign_key in enumerate(self.zodiac_data.keys())
            } 
        else:
            self.sign_longitudes = {}
            logger.error("Zodiac data not loaded, sign longitudes will be empty.")
        
        logger.info("HoroscopeService initialized successfully.")
        self._initialized = True # Mark as initialized

    def _calculate_transits_to_sun(self, sun_longitude: float) -> List[Dict[str, Any]]:
        """Calculates aspects from current planets to a given Sun longitude."""
        now_utc = datetime.now(timezone.utc)
        
        # IMPORTANT: Use self.astrology_service.get_natal_chart_details
        transit_chart = self.astrology_service.get_natal_chart_details(
            datetime_str=now_utc.isoformat(),
            timezone_str="UTC",
            latitude=51.4779, # Use a fixed location for general transits
            longitude=0.0,    # (Greenwich, UK)
            house_system="Placidus"
        )
        if 'error' in transit_chart: 
            logger.error(f"Error getting transit chart for horoscope: {transit_chart.get('error')}")
            return []

        active_aspects = []
        # Filter for actual planets that have general themes defined
        transiting_planets = {k: v for k, v in transit_chart['points'].items() if k.lower() in self.general_themes}

        for planet_name, planet_data in transiting_planets.items():
            separation = abs(planet_data['longitude'] - sun_longitude)
            # Normalize separation to be within 0-180 degrees
            if separation > 180:
                separation = 360 - separation

            for aspect_key, aspect_info in self.aspect_interpretations.items(): 
                aspect_angle = aspect_info.get('angle') 
                aspect_orb = aspect_info.get('orb', 5.0) 

                if aspect_angle is not None and abs(separation - aspect_angle) <= aspect_orb:
                    active_aspects.append({
                        "transiting_planet": planet_name,
                        "aspect_type": aspect_key, # Use key here
                        "theme_snippet": self.general_themes.get(planet_name.lower(), "N/A"), # Use lower() for key
                        "aspect_snippet": aspect_info.get('meaning', "N/A") 
                    })
        return active_aspects

    def generate_daily_horoscope(self, zodiac_sign_key: str, target_date: date) -> Dict[str, Any]:
        """
        Public facade to generate a dynamic daily horoscope for a specific sign.
        """
        logger.info(f"Generating daily horoscope for {zodiac_sign_key} for {target_date.isoformat()}.")
        
        sign_key_lower = zodiac_sign_key.lower()
        if sign_key_lower not in self.zodiac_data: 
            return {"error": f"Invalid zodiac sign '{zodiac_sign_key}' provided."}

        try:
            sign_name = self.zodiac_data[sign_key_lower]['name']
            sun_longitude = self.sign_longitudes[sign_key_lower]
            
            active_transits = self._calculate_transits_to_sun(sun_longitude)

            if not active_transits:
                horoscope_text = f"The cosmic energies are relatively quiet for {sign_name} today. It's a good day for steady progress and sticking to your routine. Focus on the fundamentals and prepare for the more dynamic days ahead."
            else:
                intro = f"For {sign_name} today, several key themes are at play. "
                # Ensure keys exist before accessing
                body_parts = [
                    f"{transit.get('theme_snippet', 'N/A')} {transit.get('aspect_snippet', 'N/A')}"
                    for transit in active_transits
                ]
                horoscope_text = intro + " ".join(body_parts) if body_parts else intro + "No significant astrological influences detected."

            return {
                "zodiac_sign": sign_name,
                "date": target_date.isoformat(),
                "horoscope_text": horoscope_text,
                "influences": active_transits
            }

        except Exception as e:
            logger.critical(f"An unexpected error occurred generating horoscope for {zodiac_sign_key}: {e}", exc_info=True)
            return {"error": "An internal server error occurred while generating the horoscope."}

    def generate_daily_horoscope_content(self, sign_key: str, user_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Public method, potentially called by controllers. Calls the core generation logic.
        """
        return self.generate_daily_horoscope(sign_key, date.today())