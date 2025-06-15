# app/services/ritual_service.py
"""
Personalized Ritual Suggestion Service

This service dynamically generates personalized ritual suggestions by fetching
structured content and merging it with user-specific astrological data.
"""
import logging
from typing import Dict, Any

# Import the content fetchers for both ritual content and zodiac data
from app.services.content_fetch_service import get_ritual_content, get_zodiac_signs_data

logger = logging.getLogger(__name__)

class RitualGeneratorService:
    """
    A service class to manage the generation of personalized rituals.
    It loads the base content once and reuses it for each request.
    """
    def __init__(self):
        logger.info("Initializing RitualGeneratorService...")
        self.ritual_content = get_ritual_content()
        self.zodiac_data = get_zodiac_signs_data()
        if not self.ritual_content or not self.zodiac_data:
            logger.error("Failed to load ritual or zodiac content. Service may not function correctly.")
            raise RuntimeError("Could not load necessary content files for Ritual service.")

    def generate_ritual(self, purpose: str, zodiac_sign_key: str) -> Dict[str, Any]:
        """
        Generates a complete, personalized ritual suggestion.

        Args:
            purpose: The key for the desired ritual (e.g., 'new-moon').
            zodiac_sign_key: The key for the user's zodiac sign (e.g., 'leo').

        Returns:
            A dictionary containing the full ritual plan or an error message.
        """
        logger.info(f"Generating ritual for purpose '{purpose}' and sign '{zodiac_sign_key}'.")
        
        # 1. Validate inputs against loaded content
        if purpose not in self.ritual_content.get("rituals", {}):
            return {"error": f"Invalid ritual purpose '{purpose}' provided."}
        if zodiac_sign_key not in self.zodiac_data:
            return {"error": f"Invalid zodiac sign '{zodiac_sign_key}' provided."}

        # 2. Get the base templates and specific user data
        base_ritual = self.ritual_content["rituals"][purpose]
        sign_data = self.zodiac_data[zodiac_sign_key]
        sign_element = sign_data.get("element")

        # 3. Dynamically create the personalized content
        personalized_title = base_ritual["title_template"].format(sign_name=sign_data["name"])
        elemental_enhancement = self.ritual_content["elemental_enhancements"].get(sign_element, "")

        # 4. Assemble the final, complete ritual object
        return {
            "title": personalized_title,
            "description": base_ritual.get("description", ""),
            "sign_context": {
                "name": sign_data.get("name"),
                "symbol": sign_data.get("symbol"),
                "element": sign_data.get("element"),
                "modality": sign_data.get("modality")
            },
            "purpose": purpose,
            "general_preparation": self.ritual_content.get("general_preparation", []),
            "steps": base_ritual.get("steps", []),
            "elemental_enhancement": elemental_enhancement,
            "safety_note": self.ritual_content.get("safety_note", "")
        }

# --- Create a single, shared instance for the application's lifetime ---
try:
    ritual_service_instance = RitualGeneratorService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate RitualGeneratorService: {e}")
    ritual_service_instance = None # Ensure it exists but is non-functional