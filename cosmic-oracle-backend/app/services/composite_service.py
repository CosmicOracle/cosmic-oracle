# app/services/composite_service.py
"""
Composite Chart Service

This service calculates a composite chart for two individuals, which represents
the relationship itself as a separate entity. It is created by finding the
midpoint between each pair of planets from the two natal charts.
"""
import logging
from typing import Dict, Any, List, Optional
import math

# --- REUSE: Import existing services and utilities ---
from app.services.astrology_service import get_natal_chart_details, astro_data_cache, AstrologyEngine

logger = logging.getLogger(__name__)

# --- Composite Chart Specific Logic ---

def _calculate_midpoint(lon1: float, lon2: float) -> float:
    """
    Calculates the shortest-arc midpoint between two longitudinal degrees.
    Handles the 360-degree wrap-around (e.g., midpoint of 350° and 10° is 0°).
    """
    diff = abs(lon1 - lon2)
    if diff > 180:
        # The shortest arc crosses the 0°/360° boundary
        if lon1 > lon2:
            lon1, lon2 = lon2, lon1 # Ensure lon1 is smaller
        mid = ((lon1 + 360) + lon2) / 2.0
        return mid % 360
    else:
        # The shortest arc is the direct one
        return (lon1 + lon2) / 2.0

def calculate_composite_chart(person_a_data: Dict[str, Any], person_b_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public facade function for the Composite Chart service.

    Args:
        person_a_data: A dictionary with birth data for the first person.
        person_b_data: A dictionary with birth data for the second person.

    Returns:
        A dictionary containing the full composite chart or an error.
    """
    logger.info("Composite service: calculating relationship chart.")
    try:
        # Step 1: Generate the two individual natal charts.
        chart_a = get_natal_chart_details(**person_a_data)
        if 'error' in chart_a:
            return {"error": f"Could not calculate chart for Person A: {chart_a['error']}"}

        chart_b = get_natal_chart_details(**person_b_data)
        if 'error' in chart_b:
            return {"error": f"Could not calculate chart for Person B: {chart_b['error']}"}

        # Step 2: Calculate the midpoints for all planets.
        composite_points_raw = {}
        for planet_name in chart_a['points']:
            if planet_name in chart_b['points']:
                lon_a = chart_a['points'][planet_name]['longitude']
                lon_b = chart_b['points'][planet_name]['longitude']
                composite_points_raw[planet_name] = _calculate_midpoint(lon_a, lon_b)
        
        # Step 3: Calculate the midpoint for the Ascendant and Midheaven.
        # This forms the axis for the composite chart's houses.
        composite_asc_lon = _calculate_midpoint(chart_a['angles']['Ascendant']['longitude'], chart_b['angles']['Ascendant']['longitude'])
        composite_mc_lon = _calculate_midpoint(chart_a['angles']['Midheaven']['longitude'], chart_b['angles']['Midheaven']['longitude'])

        # Step 4: Create a dummy "birth" moment for the composite chart.
        # This is a conceptual step. We create a dummy AstrologyEngine instance
        # primarily to use its formatting and house calculation methods. The date/time
        # doesn't matter, but the location can be the midpoint of the two birthplaces.
        composite_lat = (person_a_data['latitude'] + person_b_data['latitude']) / 2.0
        composite_lon = (person_a_data['longitude'] + person_b_data['longitude']) / 2.0 # simplified
        
        # We need a dummy UTC datetime to initialize the engine.
        dummy_utc_dt = datetime.datetime.now(datetime.timezone.utc)
        
        # We use a dummy engine to re-use the formatting and calculation logic.
        # We will override its calculated values with our midpoints.
        formatter_engine = AstrologyEngine(
            dt_utc=dummy_utc_dt,
            latitude=composite_lat,
            longitude=composite_lon,
            altitude=0,
            house_system="Placidus" # Or any preferred system
        )

        # Step 5: Format the composite points and calculate their house placements.
        # First, calculate the composite houses based on the composite Asc/MC.
        # This is a complex step; for a robust implementation, we generate houses
        # based on the composite MC and Ascendant longitudes. A simpler method is to
        # calculate the midpoint of each house cusp.
        composite_house_cusps = {}
        for i in range(1, 13):
            cusp_a_lon = chart_a['house_cusps'][i]['longitude']
            cusp_b_lon = chart_b['house_cusps'][i]['longitude']
            composite_cusp_lon = _calculate_midpoint(cusp_a_lon, cusp_b_lon)
            composite_house_cusps[i] = formatter_engine._format_point(f"House {i} Cusp", composite_cusp_lon)

        # Now format the planets and place them in the composite houses.
        composite_points = {}
        for name, lon in composite_points_raw.items():
            formatted_point = formatter_engine._format_point(name, lon)
            formatted_point['house'] = formatter_engine._determine_house_placement(lon, composite_house_cusps)
            composite_points[name] = formatted_point

        # Format the composite angles.
        composite_angles = {
            "Ascendant": {**formatter_engine._format_point("Ascendant", composite_asc_lon), "house": 1},
            "Midheaven": {**formatter_engine._format_point("Midheaven", composite_mc_lon), "house": 10},
            "Descendant": {**formatter_engine._format_point("Descendant", (composite_asc_lon + 180) % 360), "house": 7},
            "Imum Coeli": {**formatter_engine._format_point("Imum Coeli", (composite_mc_lon + 180) % 360), "house": 4}
        }
        
        # Step 6: Calculate aspects for the new composite chart.
        all_composite_points_map = {p['key']: p for p in list(composite_points.values()) + list(composite_angles.values())}
        composite_aspects = formatter_engine._calculate_aspects(all_composite_points_map)

        # Step 7: Assemble the final composite chart object.
        return {
            "composite_chart": {
                "points": composite_points,
                "angles": composite_angles,
                "house_cusps": composite_house_cusps,
                "aspects": composite_aspects,
            },
            "metadata": {
                "type": "Composite Chart (Midpoint Method)",
                "person_a_info": chart_a['chart_info'],
                "person_b_info": chart_b['chart_info'],
            }
        }

    except Exception as e:
        logger.critical(f"An unexpected fatal error occurred in the composite service: {e}", exc_info=True)
        return {"error": "An unexpected internal server error occurred during composite chart calculation."}