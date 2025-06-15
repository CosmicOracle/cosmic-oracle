# app/services/arabic_parts_service.py
"""
Arabic Parts (Lots) Calculation Service

This service calculates the positions of various traditional Arabic Parts,
or Lots, for a given natal chart.
"""
import logging
from typing import Dict, Any, List, Optional

# --- REUSE: Import the primary astrology service and a helper class ---
from app.services.astrology_service import get_natal_chart_details, AstrologyEngine
from app.services.content_fetch_service import get_arabic_parts_formulas, get_arabic_parts_interpretations

logger = logging.getLogger(__name__)

class ArabicPartsService:
    """
    A singleton service that loads Arabic Part formulas and interpretations
    and provides the logic to calculate them for a given chart.
    """
    _instance = None

    def __init__(self):
        logger.info("Initializing ArabicPartsService singleton...")
        self.formulas = get_arabic_parts_formulas().get("parts", {})
        self.interpretations = get_arabic_parts_interpretations().get("interpretations", {})
        if not self.formulas or not self.interpretations:
            raise RuntimeError("Could not load necessary Arabic Parts content files.")
        logger.info(f"ArabicPartsService initialized successfully with {len(self.formulas)} formulas.")

    def _get_required_points(self) -> set:
        """Dynamically determines the set of all unique points needed for all formulas."""
        required = set()
        for part_info in self.formulas.values():
            for point in part_info.get("day", []):
                required.add(point)
            for point in part_info.get("night", []):
                required.add(point)
        return required

    def calculate_all_parts(self, natal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public facade to generate a full Arabic Parts report for a natal chart.
        """
        logger.info("Calculating all Arabic Parts.")
        try:
            # Step 1: Generate the base natal chart.
            chart = get_natal_chart_details(**natal_data)
            if 'error' in chart:
                return {"error": f"Could not calculate base natal chart: {chart['error']}"}

            # Step 2: Determine if it's a Day or Night chart.
            sun_house = chart.get('points', {}).get('Sun', {}).get('house')
            if sun_house is None:
                return {"error": "Could not determine Sun's house to establish Day/Night chart."}
            is_day_chart = 7 <= sun_house <= 12

            # Step 3: Create a lookup table of all available point longitudes.
            # This is where the recursive calculation of parts like 'Part of Love' happens.
            available_points = {}
            for planet, data in chart.get('points', {}).items():
                available_points[planet] = data.get('longitude')
            for angle, data in chart.get('angles', {}).items():
                available_points[angle] = data.get('longitude')

            # Step 4: Iteratively calculate all parts.
            # We loop multiple times to handle parts that depend on other parts (e.g., Part of Love).
            calculated_parts = {}
            parts_to_calculate = self.formulas.copy()
            for _ in range(5): # Loop a few times to resolve dependencies
                remaining_parts = {}
                for name, info in parts_to_calculate.items():
                    formula = info.get("day") if is_day_chart else info.get("night")
                    p1_name, p2_name, p3_name = formula
                    
                    if p1_name in available_points and p2_name in available_points and p3_name in available_points:
                        part_lon = (available_points[p1_name] + available_points[p2_name] - available_points[p3_name] + 360) % 360
                        available_points[name] = part_lon # Make it available for the next iteration
                        
                        # Use a dummy engine just for formatting and house placement
                        dummy_engine = AstrologyEngine(chart['chart_info']['datetime_utc'], chart['chart_info']['latitude'], chart['chart_info']['longitude'], 0, natal_data['house_system'])
                        formatted_part = dummy_engine._format_point(name, part_lon)
                        formatted_part['house'] = dummy_engine._determine_house_placement(part_lon, chart['house_cusps'])
                        
                        # Add interpretation
                        interp_data = self.interpretations.get(info['key'], {})
                        formatted_part['interpretation'] = {
                            "title": interp_data.get("title", name),
                            "summary": interp_data.get("summary", ""),
                            "by_house": interp_data.get(f"house_{formatted_part['house']}", "No specific interpretation for this house.")
                        }
                        
                        calculated_parts[name] = formatted_part
                    else:
                        remaining_parts[name] = info
                
                if not remaining_parts: break # All parts calculated
                parts_to_calculate = remaining_parts

            return {
                "arabic_parts_report": {
                    "chart_type": "Day Chart" if is_day_chart else "Night Chart",
                    "parts": list(calculated_parts.values())
                },
                "natal_chart_used": chart['chart_info']
            }
        except Exception as e:
            logger.critical(f"An unexpected fatal error in the Arabic Parts service: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred during calculation."}

# --- Create a single, shared instance for the application's lifetime ---
try:
    arabic_parts_service_instance = ArabicPartsService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate ArabicPartsService: {e}")
    arabic_parts_service_instance = None