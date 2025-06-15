# app/services/crystal_service.py
"""
Crystal Recommendation Service

This service provides personalized crystal recommendations based on user needs,
zodiac signs, or a combination of both.
"""
import logging
from typing import Dict, Any, List, Optional

from app.services.content_fetch_service import get_crystal_content, get_zodiac_signs_data

logger = logging.getLogger(__name__)

class CrystalService:
    """
    A singleton service class that manages crystal data and provides
    recommendation logic. It pre-processes data for efficient lookups.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CrystalService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing CrystalService singleton...")
        crystal_data = get_crystal_content().get("crystals", {})
        self.zodiac_data = get_zodiac_signs_data()
        
        # --- The Performance Upgrade: Create a fast lookup table ---
        self.crystal_lookup: Dict[str, Dict[str, Any]] = {}
        for category, crystals in crystal_data.items():
            for crystal in crystals:
                # Store by lowercase name for case-insensitive matching
                self.crystal_lookup[crystal["name"].lower()] = crystal

        if not self.crystal_lookup or not self.zodiac_data:
            raise RuntimeError("Could not load necessary crystal or zodiac content files.")

        self._initialized = True
        logger.info("CrystalService initialized successfully with pre-processed lookup table.")

    def get_recommendations(self, need_key: Optional[str] = None, zodiac_sign_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates crystal recommendations based on specified criteria.
        """
        if not self._initialized:
            return {"error": "Crystal service is not available."}
        if not need_key and not zodiac_sign_key:
            return {"error": "At least one criterion (need_key or zodiac_sign_key) must be provided."}

        recommendations: Dict[str, Dict[str, Any]] = {}

        # Layer 1: Recommendations based on NEED (primary reason)
        if need_key:
            need_key_lower = need_key.lower()
            # This logic needs to be based on the new JSON structure. We'll search for it.
            crystals_for_need = []
            for crystal in self.crystal_lookup.values():
                 # A better JSON would have a `needs` array, but we can search properties
                if need_key_lower in crystal.get("properties", "").lower():
                     crystals_for_need.append(crystal)

            for crystal in crystals_for_need:
                rec = crystal.copy()
                rec["reason"] = f"Supports the need for '{need_key.replace('-', ' ').title()}'."
                recommendations[crystal["name"].lower()] = rec
        
        # Layer 2: Recommendations based on ZODIAC SIGN
        if zodiac_sign_key:
            sign_info = self.zodiac_data.get(zodiac_sign_key.lower())
            if not sign_info:
                return {"error": f"Zodiac sign '{zodiac_sign_key}' not found."}
            
            # Find crystals associated with this sign
            crystals_for_sign = []
            for crystal in self.crystal_lookup.values():
                if sign_info["name"] in crystal.get("zodiac_associations", []):
                    crystals_for_sign.append(crystal)
            
            for crystal in crystals_for_sign:
                crystal_name_lower = crystal["name"].lower()
                if crystal_name_lower in recommendations:
                    # It's already there from a 'need' match, so append the reason.
                    recommendations[crystal_name_lower]["reason"] += f" Also resonates strongly with {sign_info['name']}."
                else:
                    # Add it fresh with the zodiac reason.
                    rec = crystal.copy()
                    rec["reason"] = f"Resonates with the energy of {sign_info['name']}."
                    recommendations[crystal_name_lower] = rec
        
        return {"recommendations": list(recommendations.values())}

# --- Create a single, shared instance for the application's lifetime ---
try:
    crystal_service_instance = CrystalService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate CrystalService: {e}")
    crystal_service_instance = None