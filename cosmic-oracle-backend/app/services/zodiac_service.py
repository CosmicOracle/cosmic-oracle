# app/services/zodiac_service.py
"""
Zodiac Information and Compatibility Service
"""
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.repositories import user_preferences_repository
from app.services.content_fetch_service import get_zodiac_content, get_compatibility_content

logger = logging.getLogger(__name__)

class ZodiacService:
    """A singleton service to provide detailed information about the Zodiac."""
    _instance = None
    
    def __init__(self):
        logger.info("Initializing ZodiacService singleton...")
        self.zodiac_content = get_zodiac_content()
        self.compatibility_content = get_compatibility_content()
        if not self.zodiac_content or not self.compatibility_content:
            raise RuntimeError("Could not load necessary zodiac or compatibility content.")
        logger.info("ZodiacService initialized successfully.")

    def get_all_signs(self) -> List[Dict[str, Any]]:
        """Returns a summary list of all 12 zodiac signs."""
        return list(self.zodiac_content.get("signs", {}).values())

    def get_sign_details(self, sign_key: str) -> Dict[str, Any]:
        """Returns detailed information for a single zodiac sign."""
        sign_info = self.zodiac_content.get("signs", {}).get(sign_key.lower())
        return sign_info or {"error": "Sign not found."}

    def get_element_details(self, element_key: str) -> Dict[str, Any]:
        """Returns details for a specific element."""
        return self.zodiac_content.get("elements", {}).get(element_key.lower(), {"error": "Element not found."})

    def get_modality_details(self, modality_key: str) -> Dict[str, Any]:
        """Returns details for a specific modality."""
        return self.zodiac_content.get("modalities", {}).get(modality_key.lower(), {"error": "Modality not found."})

    def get_compatibility(self, sign1_key: str, sign2_key: str) -> Dict[str, Any]:
        """Calculates and interprets compatibility between two signs."""
        s1 = sign1_key.lower()
        s2 = sign2_key.lower()
        matrix = self.compatibility_content.get("matrix", {})
        interps = self.compatibility_content.get("rating_interpretations", {})
        
        # Check both A-B and B-A for the rating
        rating_data = matrix.get(s1, {}).get(s2) or matrix.get(s2, {}).get(s1)
        if not rating_data:
            return {"error": f"Compatibility rating for {s1}/{s2} not found."}

        rating_text = rating_data.get("rating", "Neutral")
        return {
            "sign1": self.get_sign_details(s1).get("name"),
            "sign2": self.get_sign_details(s2).get("name"),
            "rating": rating_text,
            "score": rating_data.get("score"),
            "summary": interps.get(rating_text, "A complex and unique dynamic.")
        }
        
    def get_user_preferences(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Retrieves a user's preferences via the repository."""
        prefs = user_preferences_repository.find_or_create(db, user_id)
        # Convert model object to a clean dictionary for the API
        return { "preferred_house_system": prefs.preferred_house_system, "preferred_zodiac_system": prefs.preferred_zodiac_system }

    def update_user_preferences(self, db: Session, user_id: int, preferences: Dict) -> Dict[str, Any]:
        """Updates a user's preferences via the repository."""
        updated_prefs = user_preferences_repository.update(db, user_id, preferences)
        return { "preferred_house_system": updated_prefs.preferred_house_system, "preferred_zodiac_system": updated_prefs.preferred_zodiac_system }

try:
    zodiac_service_instance = ZodiacService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate ZodiacService: {e}")
    zodiac_service_instance = None