# app/services/antiscia_service.py
"""
Antiscia and Contra-Antiscia Calculation Service

This service calculates the "shadow" or "reflection" points of celestial bodies
across the solstitial (Cancer-Capricorn) and equinoctial (Aries-Libra) axes.
These are advanced techniques used in traditional and horary astrology.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

# REUSE: Import the core natal chart service to get planetary positions
from app.services.astrology_service import get_natal_chart_details

logger = logging.getLogger(__name__)

def calculate_antiscia_and_contra_antiscia(natal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public facade function for the Antiscia service.

    Args:
        natal_data: A dictionary containing the user's birth data.

    Returns:
        A dictionary containing the full antiscia analysis or an error.
    """
    logger.info("Antiscia service: performing calculations.")
    try:
        # Step 1: Generate the base natal chart to get all point longitudes.
        chart = get_natal_chart_details(**natal_data)
        if 'error' in chart:
            return {"error": f"Could not calculate base natal chart for antiscia: {chart['error']}"}

        # Combine planets and angles into a single list for processing
        all_points = list(chart['points'].values()) + list(chart['angles'].values())

        antiscia_results = []
        contra_antiscia_results = []

        # Step 2: Iterate through each point to calculate its reflections.
        for point in all_points:
            original_lon = point.get('longitude')
            if original_lon is None: continue # Skip points without a longitude

            # --- Antiscia Calculation (Reflection across 0° Cancer / 0° Capricorn) ---
            # This is equivalent to `360 - (longitude - 90) + 90`, simplified.
            # A more intuitive formula is to find the distance from the closest solstice point
            # (90° or 270°) and apply it to the other side.
            # Simplified: The sum of a point and its antiscion is always 360, but relative
            # to the start of Cancer (90 degrees). So, it's 270 - (lon - 90) = 360 - lon
            # but that's the contra-antiscion. Let's use the standard definition.
            # Longitude (L). Midpoint of L and its Antiscia (A) is 90° or 270°.
            # If L is in Aries-Virgo (0-180): (L+A)/2 = 90  => A = 180-L
            # If L is in Libra-Pisces (180-360): (L+A)/2 = 270 => A = 540-L
            if original_lon <= 180:
                antiscia_lon = (180 - original_lon + 360) % 360
            else:
                antiscia_lon = (540 - original_lon + 360) % 360
            
            antiscia_results.append({
                "original_point": point['name'],
                "original_longitude": round(original_lon, 4),
                "antiscia_longitude": round(antiscia_lon, 4)
            })

            # --- Contra-Antiscia Calculation (Reflection across 0° Aries / 0° Libra) ---
            # This is a simple reflection across the 0°/180° axis.
            contra_antiscia_lon = (360 - original_lon) % 360
            contra_antiscia_results.append({
                "original_point": point['name'],
                "original_longitude": round(original_lon, 4),
                "contra_antiscia_longitude": round(contra_antiscia_lon, 4)
            })

        return {
            "antiscia_analysis": {
                "antiscia_points": sorted(antiscia_results, key=lambda x: x['original_longitude']),
                "contra_antiscia_points": sorted(contra_antiscia_results, key=lambda x: x['original_longitude'])
            },
            "natal_chart_used": chart['chart_info']
        }

    except Exception as e:
        logger.critical(f"An unexpected fatal error in the antiscia service: {e}", exc_info=True)
        return {"error": "An unexpected internal server error occurred during antiscia calculation."}