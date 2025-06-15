# app/services/aspect_service.py
"""
Centralized Aspect Calculation Service

This service provides a consistent, data-driven engine for calculating all
astrological aspects between a set of celestial bodies. It is designed to be
reused by other services like Natal, Synastry, and Transits.
"""
import logging
from typing import Dict, Any, List, Optional

from app.services.content_fetch_service import get_aspect_content

logger = logging.getLogger(__name__)

class AspectService:
    """
    A singleton service that loads aspect definitions and performs calculations.
    """
    _instance = None

    def __init__(self):
        logger.info("Initializing AspectService singleton...")
        self.aspect_definitions = get_aspect_content().get("aspects", [])
        if not self.aspect_definitions:
            raise RuntimeError("Could not load necessary aspect content file.")
        logger.info(f"AspectService initialized successfully with {len(self.aspect_definitions)} aspect definitions.")

    def _is_applying(self, p1: Dict[str, Any], p2: Dict[str, Any]) -> Optional[bool]:
        """
        Determines if an aspect is applying (getting closer) or separating.
        Returns True if applying, False if separating, None if speeds are unavailable or equal.
        """
        s1 = p1.get("speed_longitude")
        s2 = p2.get("speed_longitude")
        if s1 is None or s2 is None or s1 == s2:
            return None
        
        # The faster planet must be "behind" the slower planet for the aspect to be applying.
        # This logic handles the wrap-around at 360 degrees.
        if s1 > s2: # p1 is the faster planet
            return (p2['longitude'] - p1['longitude'] + 360) % 360 < 180
        else: # p2 is the faster planet
            return (p1['longitude'] - p2['longitude'] + 360) % 360 < 180

    def find_all_aspects(self, points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Finds all defined aspects between a list of celestial points.

        Args:
            points: A list of dictionaries, where each dict represents a celestial
                    body and must contain 'name', 'longitude', and optionally 'speed_longitude'.

        Returns:
            A list of all found aspects, sorted by orb.
        """
        if not self._instance: # Safety check if singleton wasn't created
             return []

        found_aspects = []
        point_pairs = [(points[i], points[j]) for i in range(len(points)) for j in range(i + 1, len(points))]

        for p1, p2 in point_pairs:
            lon1, lon2 = p1.get('longitude'), p2.get('longitude')
            if lon1 is None or lon2 is None: continue

            separation = abs(lon1 - lon2)
            if separation > 180:
                separation = 360 - separation

            for aspect_def in self.aspect_definitions:
                orb = abs(separation - aspect_def["angle"])
                if orb <= aspect_def["orb"]:
                    found_aspects.append({
                        "point1_name": p1["name"],
                        "point2_name": p2["name"],
                        "aspect_name": aspect_def["name"],
                        "aspect_type": aspect_def["type"],
                        "orb_degrees": round(orb, 3),
                        "is_applying": self._is_applying(p1, p2)
                    })

        return sorted(found_aspects, key=lambda x: x['orb_degrees'])

# --- Create a single, shared instance for the application's lifetime ---
try:
    aspect_service_instance = AspectService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate AspectService: {e}")
    aspect_service_instance = None