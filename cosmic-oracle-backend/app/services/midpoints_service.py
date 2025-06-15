# app/services/midpoints_service.py
"""
Astrological Midpoints Calculation Service

This service calculates midpoints between celestial bodies and analyzes the
aspects made to these sensitive points, forming a "midpoint tree".
"""
import logging
from typing import Dict, Any, List, Optional
from itertools import combinations

# --- REUSE other services ---
from app.services.astrology_service import get_natal_chart_details
from app.services.aspect_service import aspect_service_instance
from app.services.content_fetch_service import get_midpoint_content

logger = logging.getLogger(__name__)

class MidpointsService:
    """A singleton service to manage midpoint calculations and interpretations."""
    _instance = None

    def __init__(self):
        logger.info("Initializing MidpointsService singleton...")
        self.interpretations = get_midpoint_content().get("interpretations", {})
        if not self.interpretations:
            raise RuntimeError("Could not load necessary midpoint content file.")
        logger.info("MidpointsService initialized successfully.")

    def _calculate_midpoint_longitude(self, lon1: float, lon2: float) -> float:
        """Calculates the shortest-arc midpoint between two longitudes."""
        diff = abs(lon1 - lon2)
        if diff > 180:
            midpoint = (lon1 + lon2 + 360) / 2.0
        else:
            midpoint = (lon1 + lon2) / 2.0
        return midpoint % 360

    def generate_midpoint_tree(self, natal_data: Dict[str, Any], aspect_orb: float = 1.5) -> Dict[str, Any]:
        """
        Public facade to generate a full midpoint tree report.
        """
        logger.info("Generating midpoint tree.")
        try:
            # Step 1: Get the full natal chart.
            chart = get_natal_chart_details(**natal_data)
            if 'error' in chart:
                return {"error": f"Could not calculate base natal chart: {chart['error']}"}

            # Step 2: Prepare a list of points to use for midpoints.
            points_for_midpoints = list(chart.get('points', {}).values()) + list(chart.get('angles', {}).values())
            
            midpoint_tree = []

            # Step 3: Iterate through all unique pairs of points.
            for p1, p2 in combinations(points_for_midpoints, 2):
                if p1.get('longitude') is None or p2.get('longitude') is None:
                    continue

                # Step 4: Calculate the direct and indirect midpoints.
                direct_lon = self._calculate_midpoint_longitude(p1['longitude'], p2['longitude'])
                indirect_lon = (direct_lon + 180) % 360

                # Create conceptual "points" for the midpoints to feed into the aspect service.
                direct_midpoint_point = {"name": f"{p1['name']}/{p2['name']}", "longitude": direct_lon}
                indirect_midpoint_point = {"name": f"opp-{p1['name']}/{p2['name']}", "longitude": indirect_lon}
                
                # Step 5: Find aspects from all natal points to these two midpoint positions.
                # We create a temporary list of targets for the aspect service.
                aspects_to_direct = aspect_service_instance.find_all_aspects([direct_midpoint_point] + points_for_midpoints)
                aspects_to_indirect = aspect_service_instance.find_all_aspects([indirect_midpoint_point] + points_for_midpoints)
                
                # Filter for aspects that are within the specified orb and involve the midpoint.
                direct_aspect_hits = [asp for asp in aspects_to_direct if asp['orb_degrees'] <= aspect_orb and asp['point1_name'] == direct_midpoint_point['name']]
                indirect_aspect_hits = [asp for asp in aspects_to_indirect if asp['orb_degrees'] <= aspect_orb and asp['point1_name'] == indirect_midpoint_point['name']]

                if direct_aspect_hits or indirect_aspect_hits:
                    midpoint_tree.append({
                        "pair": [p1['name'], p2['name']],
                        "direct_midpoint": {"longitude": round(direct_lon, 4), "aspects": direct_aspect_hits},
                        "indirect_midpoint": {"longitude": round(indirect_lon, 4), "aspects": indirect_aspect_hits},
                    })

            return {"midpoint_tree": midpoint_tree, "natal_chart_used": chart['chart_info']}

        except Exception as e:
            logger.critical(f"An unexpected fatal error in the midpoints service: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred during midpoint calculation."}

# --- Create a single, shared instance ---
try:
    midpoints_service_instance = MidpointsService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate MidpointsService: {e}")
    midpoints_service_instance = None