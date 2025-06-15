# app/services/meditation_service.py
"""
Meditation Recommendation and Tracking Service
"""
import logging
from datetime import datetime, time, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

# --- REUSE other services and repositories ---
from app.services.moon_service import moon_service_instance
from app.services.chakra_service import generate_healing_plan # Assuming this function exists
from app.services.content_fetch_service import get_meditation_content
from app.repositories import meditation_repository

logger = logging.getLogger(__name__)

class MeditationService:
    """A singleton service for all meditation-related business logic."""
    _instance = None

    def __init__(self):
        logger.info("Initializing MeditationService singleton...")
        content = get_meditation_content()
        self.meditation_types = content.get("meditation_types", {})
        self.reasons = content.get("recommendation_reasons", {})
        if not self.meditation_types or not self.reasons:
            raise RuntimeError("Could not load necessary meditation content file.")
        logger.info("MeditationService initialized successfully.")

    def record_session(self, db: Session, user_id: int, duration: int, meditation_type: str, **kwargs) -> Dict[str, Any]:
        """Records a new meditation session for a user."""
        if meditation_type not in self.meditation_types:
            return {"error": f"Invalid meditation type '{meditation_type}'."}
        
        now = datetime.now(timezone.utc)
        start_time = kwargs.get("start_time", now - timedelta(minutes=duration))
        end_time = kwargs.get("end_time", now)
        
        try:
            session = meditation_repository.create_session(
                db=db, user_id=user_id, start_time=start_time, end_time=end_time,
                duration=duration, meditation_type=meditation_type,
                notes=kwargs.get("notes"), quality_rating=kwargs.get("quality_rating")
            )
            return {"message": "Session recorded successfully.", "session_id": session.id}
        except Exception as e:
            logger.error(f"Error recording session for user {user_id}: {e}", exc_info=True)
            return {"error": "A database error occurred while recording the session."}

    def get_optimal_times(self, target_date: date, latitude: float, longitude: float, timezone_str: str) -> Dict[str, Any]:
        """Calculates optimal meditation windows based on astronomical events."""
        optimal_windows = []
        
        # 1. Get Moon Phase
        moon_phase_result = moon_service_instance.get_moon_details(datetime.combine(target_date, time(12, 0), tzinfo=timezone.utc))
        if 'error' not in moon_phase_result:
            phase_name = moon_phase_result['phase_name']
            if phase_name in ["New Moon", "Full Moon"]:
                reason_key = "new_moon" if "New" in phase_name else "full_moon"
                optimal_windows.append({
                    "time_of_day": "Any",
                    "quality_score": 0.9,
                    "reason": self.reasons["astrological"].get(reason_key),
                    "recommended_type": self.meditation_types["mindfulness"]
                })

        # 2. Get Rise and Set times to determine Dawn and Dusk
        rise_set_result = moon_service_instance.get_moon_rise_set_times(target_date, latitude, longitude, timezone_str) # This needs to be expanded to get Sun rise/set
        # Placeholder for sun rise/set logic...
        # A full implementation would call a sun rise/set service.
        # For now, we add generic morning/evening slots.

        optimal_windows.append({
            "time_of_day": "Morning (Dawn)",
            "quality_score": 0.85,
            "reason": self.reasons["astrological"].get("dawn"),
            "recommended_type": self.meditation_types["mindfulness"]
        })
        optimal_windows.append({
            "time_of_day": "Evening (Dusk)",
            "quality_score": 0.8,
            "reason": self.reasons["astrological"].get("dusk"),
            "recommended_type": self.meditation_types["loving_kindness"]
        })

        return {"optimal_windows": sorted(optimal_windows, key=lambda x: x['quality_score'], reverse=True)}

    def get_user_history(self, db: Session, user_id: int, **kwargs) -> Dict[str, Any]:
        """Retrieves a user's paginated meditation history."""
        sessions, total = meditation_repository.find_sessions_for_user(
            db=db, user_id=user_id,
            start_date=kwargs.get("start_date"), end_date=kwargs.get("end_date"),
            limit=kwargs.get("limit", 50), offset=kwargs.get("offset", 0)
        )
        return {
            "total_sessions": total,
            "sessions": [{
                "id": s.id,
                "start_time": s.start_time.isoformat(),
                "duration": s.duration,
                "type": s.meditation_type,
                "rating": s.quality_rating
            } for s in sessions]
        }

# --- Create a single, shared instance ---
try:
    meditation_service_instance = MeditationService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate MeditationService: {e}")
    meditation_service_instance = None