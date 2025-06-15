# app/services/numerology_service.py
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class NumerologyService:
    _instance = None # For optional singleton pattern

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NumerologyService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        logger.info("NumerologyService initialized.")
        # NumerologyService might need content_fetch_service later if you add dynamic meanings
        # For now, it's simple and doesn't need to be passed a dependency.
        self._initialized = True

    def calculate_life_path(self, birth_date_str: str) -> Dict[str, Any]:
        """
        Calculates the life path number from a birth date string (YYYY-MM-DD).
        """
        try:
            birth_date = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            
            # Sum the digits of the birth date
            total_sum = sum(int(digit) for digit in str(birth_date.year) + str(birth_date.month) + str(birth_date.day))
            
            life_path = self._reduce_number(total_sum)
            
            meaning = self._get_life_path_meaning(life_path)
            
            return {
                "birth_date": birth_date_str,
                "life_path_number": life_path,
                "meaning": meaning,
                "master_number": life_path in [11, 22, 33]
            }
        except ValueError:
            logger.error(f"Invalid birth date format: {birth_date_str}. Expected YYYY-MM-DD.")
            return {"error": "Invalid birth date format. Please use YYYY-MM-DD."}
        except Exception as e:
            logger.critical(f"Error calculating life path for {birth_date_str}: {e}", exc_info=True)
            return {"error": "An unexpected error occurred during numerology calculation."}

    def _reduce_number(self, num: int) -> int:
        """Reduces a number to a single digit or a master number (11, 22, 33)."""
        while num > 9 and num not in [11, 22, 33]:
            num = sum(int(digit) for digit in str(num))
        return num

    def _get_life_path_meaning(self, life_path: int) -> str:
        """Fetches the meaning for a given life path number."""
        # In a real app, you'd fetch this from content_fetch_service or a database
        # For now, a simple lookup.
        meanings = {
            1: "The Leader: Independent, ambitious, and original. You are here to lead and innovate.",
            2: "The Harmonizer: Diplomatic, cooperative, and sensitive. You are here to bring balance and peace.",
            3: "The Communicator: Creative, expressive, and optimistic. You are here to inspire and uplift.",
            4: "The Builder: Practical, disciplined, and hard-working. You are here to create solid foundations.",
            5: "The Adventurer: Freedom-loving, adaptable, and versatile. You are here to experience and explore.",
            6: "The Nurturer: Responsible, compassionate, and family-oriented. You are here to serve and heal.",
            7: "The Seeker: Analytical, spiritual, and introspective. You are here to understand and uncover truths.",
            8: "The Achiever: Ambitious, powerful, and successful. You are here to manifest abundance.",
            9: "The Humanitarian: Compassionate, wise, and selfless. You are here to serve humanity.",
            11: "The Master Intuitive: Highly sensitive, inspiring, and insightful. You are here to enlighten.",
            22: "The Master Builder: Practical visionary, capable of grand achievements. You are here to build legacies.",
            33: "The Master Healer: Compassionate and a powerful healer. You are here to guide with unconditional love."
        }
        return meanings.get(life_path, "Meaning not found for this life path number.")

# IMPORTANT: Remove module-level instance creation
# numerology_service_instance = NumerologyService()