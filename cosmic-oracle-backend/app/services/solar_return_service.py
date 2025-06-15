# app/services/solar_return_service.py
"""
Solar Return Astrology Service

This service calculates the Solar Return chart, a predictive tool cast for the
exact moment the transiting Sun returns to its natal longitude for a given year.
This chart is believed to outline the themes for the year ahead.
"""

import logging
import datetime
from typing import Dict, Any, Optional

# --- REUSE: Import existing services and utilities ---
from app.services.astrology_service import get_natal_chart_details, swe, get_julian_day_utc, parse_datetime_with_timezone, convert_to_utc

logger = logging.getLogger(__name__)

# --- Solar Return Specific Logic ---

def _find_exact_solar_return_jd(natal_sun_lon: float, natal_dt_aware: datetime.datetime, target_year: int) -> Optional[float]:
    """
    Finds the precise Julian Day (UTC) of the solar return for a target year.
    
    This is a complex search problem. We use an iterative approach to zero in
    on the exact moment.
    """
    # Estimate the date of the solar return (it will be near the birthday)
    try:
        # We start searching from the beginning of the birthday in the target year
        search_start_dt = natal_dt_aware.replace(year=target_year, hour=0, minute=0, second=0, microsecond=0)
    except ValueError: # Handles leap years, e.g., born on Feb 29
        search_start_dt = natal_dt_aware.replace(year=target_year, month=2, day=28, hour=0, minute=0, second=0, microsecond=0)

    # Convert our search start time to Julian Day
    jd_start = get_julian_day_utc(convert_to_utc(search_start_dt))
    
    # The Sun moves about 1 degree per day. We'll search over a 2-day window.
    # We iterate minute by minute to find the crossing.
    for minute_offset in range(2 * 24 * 60): # 2 days in minutes
        current_jd = jd_start + (minute_offset / (24.0 * 60.0))
        
        # Calculate the Sun's position at this exact minute
        sun_pos_data, _, _ = swe.calc_ut(current_jd, swe.SE_SUN, swe.FLG_SWIEPH)
        current_sun_lon = sun_pos_data[0]
        
        # Calculate previous minute's position to check for crossing
        prev_jd = jd_start + ((minute_offset - 1) / (24.0 * 60.0))
        prev_sun_pos, _, _ = swe.calc_ut(prev_jd, swe.SE_SUN, swe.FLG_SWIEPH)
        previous_sun_lon = prev_sun_pos[0]
        
        # Handle the 0/360 degree crossover for Aries
        if abs(current_sun_lon - previous_sun_lon) > 180:
            if previous_sun_lon > current_sun_lon:
                previous_sun_lon -= 360
            else:
                current_sun_lon -= 360

        # Check if the natal Sun's longitude is between the last position and the current one
        if (previous_sun_lon <= natal_sun_lon <= current_sun_lon) or \
           (current_sun_lon <= natal_sun_lon <= previous_sun_lon):
            logger.info(f"Solar Return found at Julian Day: {current_jd}")
            return current_jd

    logger.error("Could not find the exact Solar Return time within the 2-day search window.")
    return None

def calculate_solar_return_chart(
    natal_data: Dict[str, Any],
    return_year: int,
    return_latitude: float,
    return_longitude: float
) -> Dict[str, Any]:
    """
    Public facade function for the Solar Return service.

    Args:
        natal_data: A dictionary with the user's birth data.
        return_year: The year for which to calculate the Solar Return.
        return_latitude: The user's geographic latitude AT THE TIME of the solar return.
        return_longitude: The user's geographic longitude AT THE TIME of the solar return.

    Returns:
        A dictionary containing the full Solar Return chart or an error.
    """
    logger.info(f"Solar Return service: calculating for year {return_year}.")
    try:
        # Step 1: Get the user's natal chart to find their exact natal Sun longitude.
        natal_chart = get_natal_chart_details(**natal_data)
        if 'error' in natal_chart:
            return {"error": f"Could not calculate base natal chart: {natal_chart['error']}"}

        natal_sun_longitude = natal_chart['points']['Sun']['longitude']
        
        # Parse the original birth datetime to use for our search
        natal_dt_aware = parse_datetime_with_timezone(natal_data['datetime_str'], natal_data['timezone_str'])
        if not natal_dt_aware:
            return {"error": "Could not parse natal datetime for Solar Return calculation."}
        
        # Step 2: Find the precise time of the Solar Return.
        solar_return_jd_utc = _find_exact_solar_return_jd(natal_sun_longitude, natal_dt_aware, return_year)
        if not solar_return_jd_utc:
            return {"error": "Failed to pinpoint the exact moment of the Solar Return."}

        # Convert the Julian Day back to a human-readable datetime string.
        # We need year, month, day, and fractional hour.
        year, month, day, hour_frac, _, _ = swe.revjul(solar_return_jd_utc, swe.GREG_CAL)
        hour = int(hour_frac)
        minute = int((hour_frac - hour) * 60)
        second = int((((hour_frac - hour) * 60) - minute) * 60)
        
        solar_return_datetime = datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
        
        # Step 3: Cast a new chart for that exact moment and for the user's location THAT YEAR.
        solar_return_chart = get_natal_chart_details(
            datetime_str=solar_return_datetime.isoformat(),
            timezone_str="UTC", # The time is already in UTC
            latitude=return_latitude,
            longitude=return_longitude,
            house_system="Placidus"
        )
        if 'error' in solar_return_chart:
            return {"error": f"Could not calculate the Solar Return chart itself: {solar_return_chart['error']}"}

        # Step 4: Assemble the final report.
        return {
            "solar_return_chart": solar_return_chart,
            "metadata": {
                "type": "Solar Return Chart",
                "return_year": return_year,
                "exact_return_time_utc": solar_return_datetime.isoformat(),
                "return_location": {"latitude": return_latitude, "longitude": return_longitude}
            },
            "natal_chart_used": natal_chart['chart_info']
        }

    except Exception as e:
        logger.critical(f"An unexpected fatal error in the solar return service: {e}", exc_info=True)
        return {"error": "An unexpected internal server error occurred during Solar Return calculation."}