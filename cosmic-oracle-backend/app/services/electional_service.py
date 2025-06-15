# app/services/electional_service.py
"""
Electional Astrology Service

This service helps users find an auspicious time to begin an endeavor by
searching through a time window and scoring potential charts against a set of
user-defined positive and negative criteria.
"""
import logging
import datetime
from typing import Dict, Any, List, Optional

# --- REUSE: Import the existing natal chart service and data cache ---
from app.services.astrology_service import get_natal_chart_details, astro_data_cache, parse_datetime_with_timezone, convert_to_utc

logger = logging.getLogger(__name__)

def _is_moon_void_of_course(chart: Dict[str, Any]) -> bool:
    """
    Private helper to determine if the Moon is Void of Course.
    Returns True if the Moon will make no more major applying aspects before
    it leaves its current sign.
    """
    moon_data = chart['points']['Moon']
    moon_lon = moon_data['longitude']
    current_sign_key = moon_data['sign_key']
    
    current_sign_index = [s['key'] for s in astro_data_cache.zodiac_signs].index(current_sign_key)
    next_sign_lon = ((current_sign_index + 1) * 30) % 360
    
    # Check for any applying aspects to other planets before the sign change
    for aspect in chart.get('aspects', []):
        if (aspect['point1_name'] == 'Moon' or aspect['point2_name'] == 'Moon') and aspect.get('is_applying'):
            other_planet = aspect['point2_name'] if aspect['point1_name'] == 'Moon' else aspect['point1_name']
            if other_planet not in ["Ascendant", "Midheaven", "Descendant", "Imum Coeli", "True Node", "Chiron"]:
                # If an applying aspect is found, the Moon is not void.
                return False
    return True

def _score_electional_chart(chart: Dict[str, Any], desired_conditions: Dict[str, Any]) -> tuple[int, List[str]]:
    """
    Scores a single chart based on a set of desired electional criteria.
    Returns a tuple of (score, reasons_for_score).
    """
    score = 0
    reasons = []

    # --- Rule 1: The Moon is Key ---
    if _is_moon_void_of_course(chart):
        score -= 100
        reasons.append("Detriment: Moon is Void of Course (-100).")
    else:
        score += 20
        reasons.append("Benefit: Moon is making aspects (+20).")

    moon_sign = chart['points']['Moon']['sign_name']
    if moon_sign in ['Taurus', 'Cancer']: # Exaltation and Rulership
        score += 15
        reasons.append(f"Benefit: Moon is well-dignified in {moon_sign} (+15).")
    
    # --- Rule 2: The Ascendant (The Start of the Matter) ---
    asc_sign = chart['angles']['Ascendant']['sign_name']
    if desired_conditions.get('desired_ascendant_signs') and asc_sign in desired_conditions['desired_ascendant_signs']:
        score += 25
        reasons.append(f"Benefit: Ascendant is in a desired sign ({asc_sign}) (+25).")

    # --- Rule 3: Strengthen a Key Planet ---
    planet_to_strengthen = desired_conditions.get('strengthen_planet')
    if planet_to_strengthen and planet_to_strengthen in chart['points']:
        planet_data = chart['points'][planet_to_strengthen]
        if planet_data['house'] in [1, 10, 7, 4]:
            score += 20
            reasons.append(f"Benefit: Key planet {planet_to_strengthen} is angular in House {planet_data['house']} (+20).")
        if planet_data['dignities'].get('status') in ['Rulership', 'Exaltation']:
            score += 15
            reasons.append(f"Benefit: Key planet {planet_to_strengthen} is dignified (+15).")

    # --- Rule 4: Avoid Negative Placements ---
    if desired_conditions.get('avoid_malefics_on_angles', True):
        for malefic in ['Mars', 'Saturn']:
            if chart['points'][malefic]['house'] in [1, 10, 7, 4]:
                score -= 30
                reasons.append(f"Detriment: Malefic {malefic} is angular in House {chart['points'][malefic]['house']} (-30).")

    return score, reasons

def find_best_electional_times(
    start_datetime_str: str,
    end_datetime_str: str,
    timezone_str: str,
    latitude: float,
    longitude: float,
    desired_conditions: Dict[str, Any],
    time_step_minutes: int = 60
) -> Dict[str, Any]:
    """
    Public facade function for the Electional service. Searches a time window
    to find the most astrologically auspicious moments.
    """
    logger.info(f"Electional service: searching for best time between {start_datetime_str} and {end_datetime_str}.")
    try:
        # Step 1: Parse and validate the time window.
        start_dt_aware = parse_datetime_with_timezone(start_datetime_str, timezone_str)
        end_dt_aware = parse_datetime_with_timezone(end_datetime_str, timezone_str)
        if not start_dt_aware or not end_dt_aware or start_dt_aware >= end_dt_aware:
            return {"error": "Invalid start or end time provided for the search window."}

        # Step 2: Iterate through the time window, calculating and scoring charts.
        best_charts = []
        current_dt = start_dt_aware
        time_delta = datetime.timedelta(minutes=time_step_minutes)

        while current_dt <= end_dt_aware:
            chart = get_natal_chart_details(
                datetime_str=current_dt.isoformat(),
                timezone_str=timezone_str,
                latitude=latitude,
                longitude=longitude,
                house_system="Regiomontanus" # Traditional for electional
            )
            if 'error' in chart:
                logger.warning(f"Skipping chart calculation for {current_dt.isoformat()} due to error: {chart['error']}")
                current_dt += time_delta
                continue

            score, reasons = _score_electional_chart(chart, desired_conditions)

            best_charts.append({
                "score": score,
                "datetime_local": current_dt.isoformat(),
                "reasons": reasons,
                "chart_summary": {
                    "ascendant": f"{int(chart['angles']['Ascendant']['degrees_in_sign'])}° {chart['angles']['Ascendant']['sign_name']}",
                    "moon": f"{int(chart['points']['Moon']['degrees_in_sign'])}° {chart['points']['Moon']['sign_name']} in House {chart['points']['Moon']['house']}",
                }
            })
            current_dt += time_delta

        # Step 3: Sort the results and return the top 5.
        if not best_charts:
            return {"error": "Could not find any valid charts in the specified time range."}
        
        sorted_charts = sorted(best_charts, key=lambda x: x['score'], reverse=True)
        
        return {
            "search_parameters": {
                "start_time": start_datetime_str,
                "end_time": end_datetime_str,
                "location": {"latitude": latitude, "longitude": longitude},
                "desired_conditions": desired_conditions
            },
            "top_electional_times": sorted_charts[:5]
        }

    except Exception as e:
        logger.critical(f"An unexpected fatal error occurred in the electional service: {e}", exc_info=True)
        return {"error": "An unexpected internal server error occurred during electional search."}