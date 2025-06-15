# app/services/declination_service.py
"""
Declination Analysis Service

This service calculates declination aspects (Parallel, Contra-Parallel) and
identifies "Out of Bounds" planets for a given natal chart.
"""
import logging
from typing import Dict, Any, List, Optional

# --- REUSE: Import the primary astrology service to get chart data ---
from app.services.astrology_service import get_natal_chart_details
from app.services.content_fetch_service import get_declination_content

logger = logging.getLogger(__name__)

# The maximum declination of the Sun, defining the "bounds".
SUN_MAX_DECLINATION = 23.436 # Using a more precise value

class DeclinationService:
    """
    A singleton service that loads declination content and provides analysis.
    """
    _instance = None

    def __init__(self):
        logger.info("Initializing DeclinationService singleton...")
        content = get_declination_content()
        self.interpretations = content.get("aspect_interpretations", {})
        self.oob_interpretation = content.get("out_of_bounds", {})
        if not self.interpretations or not self.oob_interpretation:
            raise RuntimeError("Could not load necessary declination content file.")
        logger.info("DeclinationService initialized successfully.")

    def get_declination_analysis(self, natal_data: Dict[str, Any], orb: float = 1.0) -> Dict[str, Any]:
        """
        Public facade to generate a full declination analysis for a natal chart.

        Args:
            natal_data: A dictionary containing the user's birth data.
            orb: The orb in degrees to use for parallel/contra-parallel aspects.

        Returns:
            A dictionary containing the full analysis or an error.
        """
        logger.info("Performing declination analysis.")
        try:
            # Step 1: Generate the base natal chart. We need ecliptic latitude,
            # which is part of the standard chart calculation.
            chart = get_natal_chart_details(**natal_data)
            if 'error' in chart:
                return {"error": f"Could not calculate base natal chart: {chart['error']}"}

            # Step 2: Extract declination for all points.
            # Declination is the same as ecliptic latitude in this context.
            all_points = list(chart['points'].values()) + list(chart['angles'].values())
            
            point_declinations = []
            for point in all_points:
                # Ensure the point has the necessary data. Angles might not have it.
                if 'name' in point and point.get('ecliptic_latitude') is not None:
                    point_declinations.append({
                        "name": point['name'],
                        "declination": point['ecliptic_latitude']
                    })

            if not point_declinations:
                return {"error": "No points with declination data found in the chart."}

            # Step 3: Identify Out of Bounds planets.
            out_of_bounds_planets = []
            for point in point_declinations:
                if abs(point['declination']) > SUN_MAX_DECLINATION:
                    oob_point = point.copy()
                    oob_point['interpretation'] = self.oob_interpretation
                    out_of_bounds_planets.append(oob_point)

            # Step 4: Calculate Parallel and Contra-Parallel aspects.
            parallels = []
            contra_parallels = []
            point_pairs = [(point_declinations[i], point_declinations[j]) for i in range(len(point_declinations)) for j in range(i + 1, len(point_declinations))]

            for p1, p2 in point_pairs:
                dec1, dec2 = p1['declination'], p2['declination']

                # Parallel: Same declination, same hemisphere (sign).
                if abs(dec1 - dec2) <= orb and (dec1 * dec2 >= 0):
                    parallels.append({
                        "point1_name": p1['name'],
                        "point2_name": p2['name'],
                        "orb_degrees": round(abs(dec1 - dec2), 3),
                        "interpretation": self.interpretations.get("Parallel", {})
                    })
                
                # Contra-Parallel: Same declination, opposite hemisphere.
                if abs(abs(dec1) - abs(dec2)) <= orb and (dec1 * dec2 < 0):
                    contra_parallels.append({
                        "point1_name": p1['name'],
                        "point2_name": p2['name'],
                        "orb_degrees": round(abs(abs(dec1) - abs(dec2)), 3),
                        "interpretation": self.interpretations.get("Contra-Parallel", {})
                    })

            # Step 5: Assemble the final report.
            return {
                "declination_analysis": {
                    "out_of_bounds_planets": out_of_bounds_planets,
                    "parallels": sorted(parallels, key=lambda x: x['orb_degrees']),
                    "contra_parallels": sorted(contra_parallels, key=lambda x: x['orb_degrees']),
                },
                "natal_chart_used": chart['chart_info']
            }

        except Exception as e:
            logger.critical(f"An unexpected fatal error in the declination service: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred during declination analysis."}

# --- Create a single, shared instance for the application's lifetime ---
try:
    declination_service_instance = DeclinationService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate DeclinationService: {e}")
    declination_service_instance = None