# app/services/content_fetch_service.py
"""
Service for fetching static content data from JSON files.
This centralizes access to configuration and interpretation data.
"""
import json
import os
from functools import lru_cache
import random
import logging
from typing import Optional, List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Determine the absolute path to the 'app' directory, then construct path to 'data'
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(APP_DIR, 'data')

# load_json_data can remain a standalone function (or static method) as it doesn't depend on instance state.
@lru_cache(maxsize=64)
def _load_json_data_cached(filename: str) -> Optional[dict]:
    """
    Loads a JSON data file from the app/data directory.
    Uses an absolute path to be robust regardless of where the script is run from.
    Returns None if file not found or invalid JSON.
    """
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.error(f"Data file '{filename}' not found at '{filepath}'. Ensure it exists.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Could not decode JSON from '{filename}'. Invalid JSON format: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading '{filename}': {e}")
        return None

# --- Define the ContentFetchService class ---
class ContentFetchService:
    """
    Service class for fetching static content data from JSON files.
    All content retrieval methods are encapsulated here.
    """
    _instance = None # For optional singleton pattern

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ContentFetchService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        logger.info("ContentFetchService initialized.")
        # No heavy loading in init if using lru_cache for each getter,
        # as data is loaded on first access of each getter.
        self._initialized = True

    # --- All getters are now methods ---

    def get_zodiac_signs_data(self) -> Optional[Dict[str, Any]]:
        """Returns the entire zodiac_signs.json content."""
        return _load_json_data_cached('zodiac_signs.json')

    def get_zodiac_signs_list(self) -> List[str]:
        """Returns a simple list of zodiac sign names in order."""
        signs_data = self.get_zodiac_signs_data()
        if signs_data:
            return [sign_data.get('name') for sign_data in signs_data.values() if sign_data.get('name')]
        return []

    def get_zodiac_sign_detail(self, sign_key: str) -> Optional[Dict[str, Any]]:
        """Returns details for a specific zodiac sign."""
        signs = self.get_zodiac_signs_data()
        return signs.get(sign_key.lower()) if signs and isinstance(signs, dict) else None

    def get_tarot_deck_data(self) -> Optional[Dict[str, Any]]:
        """Returns the entire tarot_deck.json content."""
        return _load_json_data_cached('tarot_deck.json')

    def get_crystal_data(self) -> Optional[Dict[str, Any]]:
        """Returns the entire crystal_data.json content."""
        return _load_json_data_cached('crystal_data.json')

    def get_crystals_for_need(self, need_key: str) -> List[Dict[str, Any]]:
        """Returns crystals for a specific need category."""
        crystals = self.get_crystal_data()
        if crystals and isinstance(crystals, dict):
            return crystals.get(need_key.lower(), [])
        return []

    def get_chakra_data(self) -> Optional[Dict[str, Any]]:
        """Returns the entire chakra_data.json content."""
        return _load_json_data_cached('chakra_data.json')

    def get_chakra_detail(self, chakra_key: str) -> Optional[Dict[str, Any]]:
        """Returns details for a specific chakra."""
        chakras = self.get_chakra_data()
        return chakras.get(chakra_key.lower()) if chakras and isinstance(chakras, dict) else None
        
    def get_dream_symbols_data(self) -> Optional[Dict[str, Any]]:
        """Returns the entire dream_symbols.json content."""
        return _load_json_data_cached('dream_symbols.json')

    def get_dream_symbol_meaning(self, symbol_key: str) -> Optional[str]:
        """Returns the meaning for a specific dream symbol."""
        symbols = self.get_dream_symbols_data()
        return symbols.get(symbol_key.lower()) if symbols and isinstance(symbols, dict) else None

    def get_affirmations_data(self) -> List[str]:
        """Returns a list of affirmations."""
        data = _load_json_data_cached('affirmations.json')
        return data.get("affirmations", []) if data and isinstance(data, dict) else []

    def get_random_affirmation(self) -> str:
        """Returns a single random affirmation."""
        affirmations = self.get_affirmations_data()
        return random.choice(affirmations) if affirmations else "Embrace the positive energy within and around you."

    def get_compatibility_matrix(self) -> Optional[Dict[str, Any]]:
        """Returns the zodiac compatibility_matrix.json content."""
        return _load_json_data_cached('compatibility_matrix.json')

    def get_planetary_base_data(self) -> Optional[Dict[str, Any]]:
        """Returns the planetary_data.json content (symbols, core influences)."""
        return _load_json_data_cached('planetary_data.json')

    def get_aspect_base_data(self) -> Optional[Dict[str, Any]]:
        """Returns the aspect_base_data.json content."""
        return _load_json_data_cached('aspect_base_data.json')

    def get_house_system_base_data(self) -> Optional[Dict[str, Any]]:
        """Returns the house_system_base_data.json content."""
        return _load_json_data_cached('house_system_base_data.json')

    def get_numerology_meanings_data(self) -> Optional[Dict[str, Any]]:
        """Returns the numerology_meanings.json content."""
        return _load_json_data_cached('numerology_meanings.json')

    def get_horoscope_interpretations_data(self) -> Optional[Dict[str, Any]]:
        """
        Returns the horoscope_interpretations.json content.
        """
        return _load_json_data_cached('horoscope_interpretations.json')

    def get_dignity_interpretations_data(self) -> Optional[Dict[str, Any]]:
        """
        Returns the dignity_interpretations.json content.
        """
        return _load_json_data_cached('dignity_interpretations.json')

    def get_part_of_fortune_interpretations_data(self) -> Optional[Dict[str, Any]]:
        """
        Returns the part_of_fortune_interpretations.json content.
        """
        return _load_json_data_cached('part_of_fortune_interpretations.json')

    def get_dashboard_content(self) -> Optional[Dict[str, Any]]:
        """
        Fetches dynamic content for the user dashboard.
        """
        return _load_json_data_cached('dashboard_content.json')

    def get_cosmic_events_data(self) -> List[Dict[str, Any]]:
        """
        Fetches a list of cosmic events data.
        """
        data = _load_json_data_cached('cosmic_events.json')
        return data if isinstance(data, list) else []

    def get_planetary_overview_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches overview data for planets, including general meanings and keywords.
        """
        return _load_json_data_cached('planetary_overview.json')

    def get_moon_phases_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches interpretative data for moon phases.
        """
        return _load_json_data_cached('moon_phases.json')

    def get_transit_interpretations_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches interpretative data for planetary transits.
        """
        return _load_json_data_cached('transit_interpretations.json')

    def get_detailed_aspect_interpretations_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches detailed interpretative data for planetary aspects.
        """
        return _load_json_data_cached('detailed_aspect_interpretations.json')

    def get_house_interpretations_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches interpretative data for astrological houses.
        """
        return _load_json_data_cached('house_interpretations.json')