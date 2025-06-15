# app/services/synastry_service.py
"""
Synastry (Relationship Astrology) Service

This service calculates the astrological interactions between two individuals'
natal charts to assess compatibility and relationship dynamics.

Architectural Pattern:
- Reuses the existing `astrology_service` to efficiently generate the two
  individual natal charts.
- The core logic of this service is to then compute the inter-chart aspects
  and house overlays, which are the essence of synastry analysis.
"""

import logging
from typing import Dict, Any, List, Optional

# --- REUSE: Import the existing, powerful natal chart service ---
from app.services.astrology_service import get_natal_chart_details, astro_data_cache

logger = logging.getLogger(__name__)

def _calculate_inter_aspects(chart_a: Dict[str, Any], chart_b: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Private helper to calculate the astrological aspects between the planets
    of person A and the planets and angles of person B.
    """
    aspect_list = []
    points_a = list(chart_a['points'].values())
    points_b = list(chart_b['points'].values()) + list(chart_b['angles'].values())
    aspect_definitions = astro_data_cache.aspects

    for p1 in points_a:
        for p2 in points_b:
            # Calculate the angular separation between the two planets
            separation = abs(p1['longitude'] - p2['longitude'])
            if separation > 180:
                separation = 360 - separation
            
            # Check against all defined aspects
            for aspect_name, aspect_info in aspect_definitions.items():
                if abs(separation - aspect_info["degrees"]) <= aspect_info["orb"]:
                    aspect_list.append({
                        "person_a_point": p1['name'],
                        "person_b_point": p2['name'],
                        "aspect_name": aspect_name,
                        "aspect_symbol": aspect_info["symbol"],
                        "orb_degrees": round(abs(separation - aspect_info["degrees"]), 3),
                    })
    
    return sorted(aspect_list, key=lambda x: x['orb_degrees'])

def _calculate_house_overlays(chart_a: Dict[str, Any], chart_b: Dict[str, Any]) -> Dict[str, int]:
    """
    Private helper to determine which of Person A's houses Person B's
    planets fall into.
    """
    overlays = {}
    house_cusps_a = chart_a['house_cusps']
    points_b = chart_b['points']

    # This is a simplified house placement function; a more robust one could be shared
    def _get_house_for_planet(planet_lon: float, cusps: Dict[int, Any]) -> Optional[int]:
        cusp_lons = [cusps[i]['longitude'] for i in range(1, 13)]
        for i in range(12):
            start_lon, end_lon = cusp_lons[i], cusp_lons[(i + 1) % 12]
            if start_lon < end_lon:
                if start_lon <= planet_lon < end_lon: return i + 1
            else: # Wraps around 0 degrees Aries
                if planet_lon >= start_lon or planet_lon < end_lon: return i + 1
        return None

    for planet_name, planet_data in points_b.items():
        house_number = _get_house_for_planet(planet_data['longitude'], house_cusps_a)
        overlays[planet_name] = house_number
    
    return overlays

def calculate_synastry_chart(person_a_data: Dict[str, Any], person_b_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public facade function for the Synastry service.

    Args:
        person_a_data: A dictionary with birth data for the first person.
        person_b_data: A dictionary with birth data for the second person.

    Returns:
        A dictionary containing the full synastry analysis or an error.
    """
    logger.info("Synastry service: calculating relationship chart.")
    try:
        # Step 1: Generate the two individual natal charts by reusing the astrology service.
        chart_a = get_natal_chart_details(**person_a_data)
        if 'error' in chart_a:
            return {"error": f"Could not calculate chart for Person A: {chart_a['error']}"}

        chart_b = get_natal_chart_details(**person_b_data)
        if 'error' in chart_b:
            return {"error": f"Could not calculate chart for Person B: {chart_b['error']}"}

        # Step 2: Perform the unique synastry calculations.
        inter_aspects = _calculate_inter_aspects(chart_a, chart_b)
        person_b_placements_in_a_houses = _calculate_house_overlays(chart_a, chart_b)
        person_a_placements_in_b_houses = _calculate_house_overlays(chart_b, chart_a)

        # Step 3: Assemble the final, comprehensive synastry report.
        synastry_report = {
            "synastry_analysis": {
                "inter_chart_aspects": inter_aspects,
                "person_b_in_person_a_houses": person_b_placements_in_a_houses,
                "person_a_in_person_b_houses": person_a_placements_in_b_houses,
            },
            "person_a_natal_chart": chart_a,
            "person_b_natal_chart": chart_b,
        }
        
        return synastry_report

    except Exception as e:
        logger.critical(f"An unexpected fatal error occurred in the synastry service: {e}", exc_info=True)
        return {"error": "An unexpected internal server error occurred during synastry calculation."}