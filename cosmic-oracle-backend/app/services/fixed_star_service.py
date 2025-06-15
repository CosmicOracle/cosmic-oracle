# app/services/fixed_star_service.py
"""
Fixed Star Astrology Service

This service provides in-depth analysis of the influence of major fixed stars
on a natal chart, including conjunctions, oppositions, and parans (paranatellonta).
"""
import logging
from typing import Dict, Any, List, Optional
import math

# --- REUSE: Import existing services and data ---
from app.services.astrology_service import get_natal_chart_details, astro_data_cache, swe

logger = logging.getLogger(__name__)

# --- Fixed Star Specific Logic ---

# Orbs for fixed star aspects are traditionally very tight.
CONJUNCTION_OPPOSITION_ORB = 1.5
PARAN_ORB_DEGREES = 0.5 # A very tight orb for simultaneous angle crossings

def _calculate_conjunctions_and_oppositions(chart_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Finds which fixed stars are conjunct or opposite the natal planets and angles.
    """
    results = []
    fixed_stars = astro_data_cache.fixed_stars

    for star in fixed_stars:
        for point in chart_points:
            # Calculate separation in longitude
            separation = abs(point['longitude'] - star['longitude'])
            if separation > 180:
                separation = 360 - separation
            
            # Check for conjunction
            if separation <= CONJUNCTION_OPPOSITION_ORB:
                results.append({
                    "type": "Conjunction",
                    "point_name": point['name'],
                    "star_name": star['name'],
                    "orb_degrees": round(separation, 3),
                    "interpretation_keywords": star['keywords']
                })

            # Check for opposition
            if abs(separation - 180) <= CONJUNCTION_OPPOSITION_ORB:
                results.append({
                    "type": "Opposition",
                    "point_name": point['name'],
                    "star_name": star['name'],
                    "orb_degrees": round(abs(separation - 180), 3),
                    "interpretation_keywords": star['keywords']
                })

    return sorted(results, key=lambda x: x['orb_degrees'])

def _calculate_parans(
    julian_day_utc: float,
    latitude: float,
    longitude: float,
    natal_planets: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Calculates the parans (paranatellonta) for a chart.
    This is a complex check for when a planet and a star cross one of the four
    cardinal angles (rising, setting, culminating, anti-culminating) at the same time.
    """
    parans = []
    fixed_stars = astro_data_cache.fixed_stars
    swe.set_topo(longitude, latitude, 0)

    for star in fixed_stars:
        # Get the times when the star is on one of the four angles for that day
        # The star name must be compatible with swisseph; we use a comma-separated format.
        star_name_swe = f"{star['name']},"
        try:
            # swe.rise_trans returns transit times for rising, setting, upper and lower culmination
            res, star_transits, err = swe.rise_trans(julian_day_utc - 0.5, swe.SE_FIXSTAR, star_name_swe, 0, swe.SE_BIT_RISE_SET_ONLY, 0.0)
            if res == -1 or not star_transits:
                continue
        except Exception:
            continue # Skip stars not in the swisseph database

        star_angle_times = {
            'rising': star_transits[0][0],
            'culminating': star_transits[1][0],
            'setting': star_transits[0][1],
            'anti-culminating': star_transits[1][1]
        }

        for planet_name, planet_id in {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN}.items():
            try:
                # Get the times the planet is on the angles for the same day
                res, planet_transits, err = swe.rise_trans(julian_day_utc - 0.5, planet_id, '', 0, swe.SE_BIT_RISE_SET_ONLY, 0.0)
                if res == -1 or not planet_transits:
                    continue
            except Exception:
                continue

            planet_angle_times = {
                'rising': planet_transits[0][0],
                'culminating': planet_transits[1][0],
                'setting': planet_transits[0][1],
                'anti-culminating': planet_transits[1][1]
            }

            # Now, compare the timestamps for each angle
            for angle, star_jd in star_angle_times.items():
                for p_angle, planet_jd in planet_angle_times.items():
                    # Calculate the time difference in minutes
                    time_diff_minutes = abs(star_jd - planet_jd) * 24 * 60
                    # Convert the paran orb from degrees to a time equivalent (1 deg = 4 min)
                    time_orb_minutes = PARAN_ORB_DEGREES * 4

                    if time_diff_minutes <= time_orb_minutes:
                        parans.append({
                            "type": "Paran",
                            "planet_name": planet_name,
                            "planet_angle": p_angle.capitalize(),
                            "star_name": star['name'],
                            "star_angle": angle.capitalize(),
                            "time_difference_minutes": round(time_diff_minutes, 2),
                            "interpretation_keywords": star['keywords']
                        })

    return parans

def get_fixed_star_analysis(natal_chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public facade function for the Fixed Star service.

    Args:
        natal_chart_data: A dictionary with birth data for the individual.

    Returns:
        A dictionary containing the full fixed star analysis or an error.
    """
    logger.info("Fixed Star service: performing analysis.")
    try:
        # Step 1: Generate the base natal chart to get planet positions.
        chart = get_natal_chart_details(**natal_chart_data)
        if 'error' in chart:
            return {"error": f"Could not calculate base natal chart: {chart['error']}"}

        all_points = list(chart['points'].values()) + list(chart['angles'].values())

        # Step 2: Perform the specialized fixed star calculations.
        conjunctions_oppositions = _calculate_conjunctions_and_oppositions(all_points)
        parans = _calculate_parans(
            chart['chart_info']['julian_day_utc'],
            chart['chart_info']['latitude'],
            chart['chart_info']['longitude'],
            chart['points']
        )

        # Step 3: Assemble the final report.
        return {
            "fixed_star_analysis": {
                "conjunctions_and_oppositions": conjunctions_oppositions,
                "parans": parans,
            },
            "natal_chart_used": chart['chart_info']
        }

    except Exception as e:
        logger.critical(f"An unexpected fatal error in the fixed star service: {e}", exc_info=True)
        return {"error": "An unexpected internal server error occurred during fixed star analysis."}