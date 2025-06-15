# app/services/horary_service.py
"""
Horary Astrology Service

This service casts and analyzes a chart for the precise moment a question is
asked, based on traditional horary rules.
"""
import logging
from typing import Dict, Any, List, Optional

# --- REUSE: Import the existing natal chart service and data cache ---
from app.services.astrology_service import get_natal_chart_details, astro_data_cache

logger = logging.getLogger(__name__)

# --- Horary Specific Logic ---

# Traditional planetary rulerships of the houses
HOUSE_RULERSHIPS = {
    1: ["life", "the querent"],
    2: ["wealth", "movable possessions"],
    3. ["siblings", "short journeys", "communication"],
    4: ["father", "home", "land", "end of life"],
    5: ["children", "pleasure", "creativity", "romance"],
    6: ["illness", "employees", "small animals"],
    7: ["partnerships", "marriage", "open enemies", "the quesited"],
    8: ["death", "inheritance", "partner's wealth"],
    9: ["long journeys", "spirituality", "higher education"],
    10: ["career", "mother", "reputation", "the king"],
    11: ["friends", "hopes and wishes"],
    12: ["self-undoing", "hidden enemies", "sorrow", "large animals"]
}

def _get_ruler_of_house(house_cusp_sign: str) -> str:
    """Finds the traditional ruler of a given sign."""
    return astro_data_cache.rulerships['rulership'].get(house_cusp_sign, "Unknown")

def _is_void_of_course(moon_data: Dict[str, Any], aspects: List[Dict[str, Any]]) -> bool:
    """
    Checks if the Moon is Void of Course (will make no more applying major
    aspects before it changes sign).
    """
    moon_lon = moon_data['longitude']
    current_sign_key = moon_data['sign_key']
    
    # Find the longitude of the next sign cusp
    current_sign_index = [s['key'] for s in astro_data_cache.zodiac_signs].index(current_sign_key)
    next_sign_lon = ((current_sign_index + 1) * 30) % 360
    degrees_to_next_sign = (next_sign_lon - moon_lon + 360) % 360
    if degrees_to_next_sign == 0: degrees_to_next_sign = 30 # Edge case on cusp

    # Check for any applying aspects to other planets before the sign change
    for aspect in aspects:
        if (aspect['point1_name'] == 'Moon' or aspect['point2_name'] == 'Moon') and aspect.get('is_applying'):
            other_planet = aspect['point2_name'] if aspect['point1_name'] == 'Moon' else aspect['point1_name']
            if other_planet not in ["Ascendant", "Midheaven", "Descendant", "Imum Coeli"]:
                # If an applying aspect is found, the Moon is not void.
                return False
                
    return True

def _check_considerations_before_judgment(chart: Dict[str, Any]) -> List[str]:
    """
    Applies traditional checks to determine if a horary chart is 'radical'
    and fit to be judged.
    """
    considerations = []
    
    asc_lon = chart['angles']['Ascendant']['longitude']
    saturn_lon = chart['points']['Saturn']['longitude']

    # 1. Is the Ascendant very early or very late?
    if asc_lon % 30 < 3:
        considerations.append("Ascendant is in the first 3 degrees of the sign: The matter may be too early to judge, or the querent may be asking frivolously.")
    if asc_lon % 30 > 27:
        considerations.append("Ascendant is in the last 3 degrees of the sign: The matter is already decided or past changing; the querent may be desperate.")

    # 2. Is Saturn in the 1st house?
    if chart['points']['Saturn']['house'] == 1:
        considerations.append("Saturn is in the 1st house: This can corrupt the chart and the querent's judgment.")

    # 3. Is Saturn in the 7th house?
    if chart['points']['Saturn']['house'] == 7:
        considerations.append("Saturn is in the 7th house: The astrologer may make an error in judgment.")

    # 4. Is the Moon Void of Course?
    if _is_void_of_course(chart['points']['Moon'], chart.get('aspects', [])):
        considerations.append("The Moon is Void of Course: 'Nothing will come of the matter.' The situation is unlikely to change or progress.")

    # 5. Via Combusta ("The Fiery Way")
    moon_lon = chart['points']['Moon']['longitude']
    if 195 <= moon_lon < 225: # 15 Libra to 15 Scorpio
        considerations.append("The Moon is in the Via Combusta (15° Libra - 15° Scorpio): This indicates a chaotic, unpredictable, or difficult situation.")
        
    return considerations

def analyze_horary_chart(
    question_topic_house: int,
    datetime_str: str,
    timezone_str: str,
    latitude: float,
    longitude: float
) -> Dict[str, Any]:
    """
    Public facade function for the Horary service.

    Args:
        question_topic_house: The number (1-12) of the house that governs the question.
        datetime_str: The exact datetime the question was posed.
        timezone_str: The timezone of the location where the question was posed.
        latitude: The latitude of the location.
        longitude: The longitude of the location.

    Returns:
        A dictionary containing the full horary analysis or an error.
    """
    logger.info(f"Horary service: calculating chart for question about house {question_topic_house}.")
    try:
        # Step 1: Generate the base chart for the moment of the question.
        # Horary traditionally uses Regiomontanus houses.
        chart = get_natal_chart_details(
            datetime_str=datetime_str,
            timezone_str=timezone_str,
            latitude=latitude,
            longitude=longitude,
            house_system="Regiomontanus"
        )
        if 'error' in chart:
            return {"error": f"Could not calculate base chart for horary: {chart['error']}"}

        # Step 2: Apply horary-specific analysis.
        considerations = _check_considerations_before_judgment(chart)
        
        # Step 3: Identify the primary significators.
        # The Querent (person asking) is represented by the ruler of the 1st house.
        asc_sign = chart['angles']['Ascendant']['sign_name']
        querent_ruler_name = _get_ruler_of_house(asc_sign)
        querent_significator = chart['points'].get(querent_ruler_name)
        
        # The Quesited (the thing being asked about) is represented by the ruler of the relevant house.
        quesited_house_cusp_sign = chart['house_cusps'][question_topic_house]['sign_name']
        quesited_ruler_name = _get_ruler_of_house(quesited_house_cusp_sign)
        quesited_significator = chart['points'].get(quesited_ruler_name)

        # Step 4: Check for a perfecting aspect between significators (the core of the answer).
        perfecting_aspect = None
        for aspect in chart.get('aspects', []):
            significators_involved = {querent_ruler_name, quesited_ruler_name}
            aspect_points = {aspect['point1_name'], aspect['point2_name']}
            
            if significators_involved == aspect_points and aspect.get('is_applying'):
                perfecting_aspect = aspect
                break # Found the most important aspect

        # Step 5: Formulate a preliminary judgment.
        judgment = ""
        if perfecting_aspect:
            aspect_type = perfecting_aspect['aspect_name']
            if aspect_type in ["conjunction", "trine", "sextile"]:
                judgment = f"Yes. The matter is likely to come to pass, signified by the applying {aspect_type} between the Querent's ruler ({querent_ruler_name}) and the Quesited's ruler ({quesited_ruler_name})."
            elif aspect_type in ["opposition", "square"]:
                judgment = f"No. The matter will be difficult or will not come to pass, signified by the challenging applying {aspect_type} between the significators."
        else:
            judgment = "No perfecting aspect was found between the significators, suggesting the matter will not come to pass or will require intervention from another party (translation of light)."

        # Step 6: Assemble the full horary report.
        return {
            "horary_analysis": {
                "considerations_before_judgment": considerations,
                "judgment_summary": judgment,
                "querent_significator": {
                    "planet": querent_ruler_name,
                    "sign": querent_significator.get('sign_name'),
                    "degree": querent_significator.get('degrees_in_sign'),
                    "house": querent_significator.get('house'),
                },
                "quesited_significator": {
                    "planet": quesited_ruler_name,
                    "sign": quesited_significator.get('sign_name'),
                    "degree": quesited_significator.get('degrees_in_sign'),
                    "house": quesited_significator.get('house'),
                },
                "perfecting_aspect": perfecting_aspect
            },
            "horary_chart": chart
        }

    except Exception as e:
        logger.critical(f"An unexpected fatal error occurred in the horary service: {e}", exc_info=True)
        return {"error": "An unexpected internal server error occurred during horary calculation."}