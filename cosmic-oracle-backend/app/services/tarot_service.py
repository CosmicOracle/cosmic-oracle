# app/services/tarot_service.py
import logging
import random
from typing import Dict, List, Any, Optional

from app.services.content_fetch_service import ContentFetchService # Import the class

logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class TarotService:
    _instance = None # Optional: Singleton pattern

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TarotService, cls).__new__(cls)
        return cls._instance

    def __init__(self, content_fetch_service_instance: ContentFetchService = None):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing TarotService...")

        if content_fetch_service_instance is None:
            raise RuntimeError("ContentFetchService instance must be provided to TarotService.")
        self.content_fetch_service = content_fetch_service_instance

        self.tarot_deck = self.content_fetch_service.get_tarot_deck_data()
        if not self.tarot_deck:
            raise RuntimeError("Tarot deck data could not be loaded. Check tarot_deck.json.")

        self._initialized = True
        logger.info("TarotService initialized successfully.")

    def _draw_cards(self, num_cards: int) -> List[Dict[str, Any]]:
        """Draws a specified number of cards from the deck."""
        all_cards = []
        if self.tarot_deck and "major_arcana" in self.tarot_deck:
            for card in self.tarot_deck["major_arcana"]:
                all_cards.append({"name": card["name"], "type": "major", "upright": card["upright"], "reversed": card.get("reversed")})
        
        if self.tarot_deck and "minor_arcana" in self.tarot_deck:
            for suit, cards in self.tarot_deck["minor_arcana"].items():
                for card in cards:
                    all_cards.append({"name": card["name"], "type": f"minor_{suit}", "upright": card["upright"], "reversed": card.get("reversed")})

        if not all_cards:
            self.logger.warning("No cards found in tarot deck data.")
            return []

        drawn_cards = random.sample(all_cards, min(num_cards, len(all_cards)))
        
        # Determine if card is upright or reversed
        for card in drawn_cards:
            card['orientation'] = "upright" if random.random() > 0.5 else "reversed"
            card['meaning'] = card['upright'] if card['orientation'] == 'upright' else card.get('reversed', card['upright']) # Fallback to upright if no reversed meaning
        
        return drawn_cards

    def perform_reading(self, spread_type: str, num_cards: int = 3) -> Dict[str, Any]:
        """
        Performs a tarot reading based on spread type and number of cards.
        """
        self.logger.info(f"Performing tarot reading for spread: {spread_type} with {num_cards} cards.")
        
        if num_cards <= 0:
            return {"error": "Number of cards must be positive."}
        
        drawn_cards = self._draw_cards(num_cards)
        if not drawn_cards:
            return {"error": "Could not draw cards. Tarot deck data might be empty or invalid."}

        # Simple interpretation based on spread type
        reading_summary = f"Your {spread_type.capitalize()} reading reveals: "
        if spread_type.lower() == "past_present_future" and num_cards >= 3:
            reading_summary += f"Past: {drawn_cards[0]['name']} ({drawn_cards[0]['orientation']}). Present: {drawn_cards[1]['name']} ({drawn_cards[1]['orientation']}). Future: {drawn_cards[2]['name']} ({drawn_cards[2]['orientation']})."
        else:
            card_names = [f"{card['name']} ({card['orientation']})" for card in drawn_cards]
            reading_summary += f"You drew: {', '.join(card_names)}. "
            reading_summary += "Consider the collective energies of these cards."
            
        detailed_meanings = [
            {"card": card["name"], "orientation": card["orientation"], "meaning": card["meaning"]}
            for card in drawn_cards
        ]

        return {
            "spread_type": spread_type,
            "cards_drawn": drawn_cards,
            "reading_summary": reading_summary,
            "detailed_meanings": detailed_meanings
        }

    # Example: A method to save readings (would interact with a database service)
    def save_reading(self, user_id: str, reading_data: Dict[str, Any]) -> bool:
        """Saves a tarot reading for a user (placeholder)."""
        self.logger.info(f"Saving reading for user {user_id}. Reading data: {reading_data['spread_type']}")
        # This is where you would call a database service to persist the data.
        # For example: self.db_service.save_tarot_reading(user_id, reading_data)
        return True # Simulate success