# cosmic-oracle-backend/app/utils.py
import datetime
import pytz # For timezone handling
import re # For potential regex use, though TIMEZONE_REGEX was unused
from typing import Optional, Tuple, Dict, Any, List
import swisseph as swe # For get_julian_day_utc calculation
import requests # For making HTTP requests in geocoding
from timezonefinder import TimezoneFinder # For finding timezone from lat/lon

# Attempt to import current_app for logging. Fallback if not in Flask context.
try:
    from flask import current_app
except ImportError:
    # Dummy logger for standalone testing or if Flask context is not available
    import logging
    class DummyApp:
        def __init__(self):
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            # Add a dummy config for APP_NAME_FOR_USER_AGENT
            self.config = {'APP_NAME_FOR_USER_AGENT': 'CosmicOracleUtils/1.0'}

    current_app = DummyApp()


# Initialize TimezoneFinder. It can be slow on first call, so global is fine.
# For multi-process servers, each process will initialize its own.
try:
    tf = TimezoneFinder()
except Exception as e:
    current_app.logger.error(f"Failed to initialize TimezoneFinder: {e}")
    tf = None # Handle gracefully if it fails

def parse_date_string(date_str: str, date_format: str = "%Y-%m-%d") -> Optional[datetime.date]:
    """
    Parses a date string into a Python date object.
    Returns None if parsing fails.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        return datetime.datetime.strptime(date_str, date_format).date()
    except ValueError:
        current_app.logger.warning(f"Invalid date string format: '{date_str}'. Expected '{date_format}'.")
        return None

def parse_time_string(time_str: str, time_format: str = "%H:%M") -> Optional[datetime.time]:
    """
    Parses a time string into a Python time object.
    Tries "HH:MM:SS" first, then "HH:MM".
    Returns None if parsing fails.
    """
    if not time_str or not isinstance(time_str, str):
        return None
    try:
        return datetime.datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        try:
            return datetime.datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            current_app.logger.warning(f"Invalid time string format: '{time_str}'. Expected 'HH:MM:SS' or 'HH:MM'.")
            return None

def combine_date_time_to_utc(date_obj: datetime.date,
                             time_obj: datetime.time,
                             timezone_str: str) -> Optional[datetime.datetime]:
    """
    Combines a date object and time object with a given local timezone string,
    and converts it to a UTC datetime object.
    Returns None if any input is invalid or conversion fails.
    """
    if not all([isinstance(date_obj, datetime.date),
                isinstance(time_obj, datetime.time),
                isinstance(timezone_str, str) and timezone_str]):
        current_app.logger.warning("Invalid input types for combine_date_time_to_utc.")
        return None

    try:
        local_tz = pytz.timezone(timezone_str)
        naive_dt = datetime.datetime.combine(date_obj, time_obj)
        # Handle ambiguous or non-existent times carefully
        local_dt = local_tz.localize(naive_dt, is_dst=None) # is_dst=None raises error for ambiguous/non-existent
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt
    except pytz.exceptions.UnknownTimeZoneError:
        current_app.logger.error(f"Unknown timezone string provided: '{timezone_str}'.")
        return None
    except (pytz.exceptions.AmbiguousTimeError, pytz.exceptions.NonExistentTimeError) as e:
        current_app.logger.error(f"Timezone error for {naive_dt} in {timezone_str}: {e}. Consider asking user for DST clarification.")
        # For non-interactive, might try is_dst=True then is_dst=False, or just fail.
        return None
    except (AttributeError, ValueError) as e: # Catch other potential issues
        current_app.logger.error(f"Error combining date/time/tz: {e}", exc_info=True)
        return None

def parse_datetime_with_timezone(datetime_str: str, timezone_str: str) -> Optional[datetime.datetime]:
    """
    Parses a datetime string (e.g., "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD HH:MM")
    and a timezone string into a timezone-aware datetime object.
    """
    if not datetime_str or not timezone_str:
        return None
    try:
        # Standardize possible "T" separator from ISO formats
        datetime_str_standardized = datetime_str.replace("T", " ")
        dt_naive = None
        possible_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
        for fmt in possible_formats:
            try:
                dt_naive = datetime.datetime.strptime(datetime_str_standardized, fmt)
                break # Success
            except ValueError:
                continue # Try next format
        
        if dt_naive is None:
            current_app.logger.warning(f"Could not parse datetime string: '{datetime_str_standardized}' with known formats.")
            return None

        tz = pytz.timezone(timezone_str)
        dt_aware = tz.localize(dt_naive, is_dst=None)
        return dt_aware
    except pytz.exceptions.UnknownTimeZoneError:
        current_app.logger.error(f"Unknown timezone string for parsing: '{timezone_str}'.")
        return None
    except (pytz.exceptions.AmbiguousTimeError, pytz.exceptions.NonExistentTimeError) as e:
        current_app.logger.error(f"Timezone error parsing datetime '{datetime_str_standardized}' in {timezone_str}: {e}.")
        return None
    except ValueError as e: # Other strptime issues not caught above
        current_app.logger.error(f"General ValueError parsing datetime string '{datetime_str_standardized}': {e}.")
        return None

def convert_to_utc(dt_aware: datetime.datetime) -> Optional[datetime.datetime]:
    """Converts a timezone-aware datetime object to UTC."""
    if not isinstance(dt_aware, datetime.datetime): return None
    if dt_aware.tzinfo is None or dt_aware.tzinfo.utcoffset(dt_aware) is None:
        current_app.logger.warning("convert_to_utc received a naive datetime object. Cannot convert to UTC without timezone info.")
        return None
    return dt_aware.astimezone(pytz.utc)

def validate_latitude(lat: Any) -> bool:
    """Validates if latitude is within the -90 to 90 range."""
    try:
        lat_float = float(lat)
        return -90.0 <= lat_float <= 90.0
    except (ValueError, TypeError):
        return False

def validate_longitude(lon: Any) -> bool:
    """Validates if longitude is within the -180 to 180 range."""
    try:
        lon_float = float(lon)
        return -180.0 <= lon_float <= 180.0
    except (ValueError, TypeError):
        return False

def get_julian_day_utc(dt: datetime.datetime) -> Optional[float]: # NAME FIXED
    """
    Converts a timezone-aware datetime object to Julian Day (UT) as required by Swiss Ephemeris.
    Returns None if input is naive or invalid.
    """
    if not isinstance(dt, datetime.datetime):
        current_app.logger.error(f"Invalid input type for get_julian_day_utc: expected datetime, got {type(dt)}")
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        current_app.logger.warning("get_julian_day_utc received a naive datetime. Cannot reliably convert to Julian Day UT.")
        return None

    dt_utc = dt.astimezone(pytz.utc) # Ensure it's explicitly UTC

    # Calculate decimal hour for swisseph
    hour_decimal = dt_utc.hour + (dt_utc.minute / 60.0) + \
                   (dt_utc.second / 3600.0) + \
                   (dt_utc.microsecond / 3600000000.0)

    try:
        # swe.GREG_CAL specifies Gregorian calendar
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal, swe.GREG_CAL)
        return jd_ut
    except Exception as e: # Catch potential errors from swisseph library itself
        current_app.logger.error(f"Error calculating Julian Day with Swiss Ephemeris: {e}", exc_info=True)
        return None

def get_zodiac_sign_from_degrees(ecliptic_longitude_degrees: float,
                                 zodiac_data_list: List[Tuple[str, str, str]]) -> Dict[str, Any]:
    """
    Determines the zodiac sign, degree within sign, and symbol from ecliptic longitude.
    zodiac_data_list: A list of tuples like [('aries', 'Aries', '♈'), ...],
                      assumed to be correctly ordered for the 12 zodiac signs and 12 items long.
    """
    if not isinstance(zodiac_data_list, list) or len(zodiac_data_list) != 12:
        current_app.logger.error("Invalid zodiac_data_list provided to get_zodiac_sign_from_degrees.")
        return {
            "key": "error", "name": "Error: Bad Zodiac Data", "symbol": "!",
            "longitude_ecliptic": round(ecliptic_longitude_degrees, 6),
            "longitude_normalized": round(ecliptic_longitude_degrees % 360.0, 6),
            "degrees_in_sign": 0.0, "display_short": "Error", "display_dms": "Error"
        }

    lon_normalized = ecliptic_longitude_degrees % 360.0
    if lon_normalized < 0: # Ensure positive range 0-359.99...
        lon_normalized += 360.0

    sign_index = int(lon_normalized // 30) # Each sign is 30 degrees
    degree_in_sign_float = lon_normalized % 30.0

    # This check should be redundant if zodiac_data_list has 12 items, but good for safety
    if 0 <= sign_index < len(zodiac_data_list):
        sign_key, sign_name, sign_symbol = zodiac_data_list[sign_index]

        # Precise DMS calculation
        deg_int = int(degree_in_sign_float)
        minutes_decimal = (degree_in_sign_float - deg_int) * 60.0
        min_int = int(minutes_decimal)
        seconds_decimal = (minutes_decimal - min_int) * 60.0
        sec_int = int(round(seconds_decimal)) # Round seconds

        # Handle cascading round-ups
        if sec_int >= 60:
            min_int += 1
            sec_int = 0
        if min_int >= 60:
            deg_int += 1
            min_int = 0
        # If deg_int becomes 30 due to rounding, it means it's practically 0 of the next sign,
        # but the sign_key/name/symbol are already correctly determined by sign_index.
        # For display, we can cap it at 29° 59' 59" for consistency within the sign.
        if deg_int >= 30:
            deg_int = 29
            min_int = 59
            sec_int = 59
            current_app.logger.debug(f"DMS calculation for lon {ecliptic_longitude_degrees} resulted in degree >=30, capped to 29°59'59\" of {sign_name}")


        sign_display_dms = f"{deg_int}°{sign_symbol}{min_int:02d}'{sec_int:02d}\""

        return {
            "key": sign_key,
            "name": sign_name,
            "symbol": sign_symbol,
            "longitude_ecliptic": round(ecliptic_longitude_degrees, 6),
            "longitude_normalized": round(lon_normalized, 6),
            "degrees_in_sign": round(degree_in_sign_float, 6), # Store with more precision
            "display_short": f"{degree_in_sign_float:.2f}° {sign_symbol}", # Display rounded
            "display_dms": sign_display_dms
        }

    current_app.logger.error(f"Could not determine zodiac sign for ecliptic longitude {ecliptic_longitude_degrees}. Calculated index {sign_index} is out of range for zodiac data list.")
    return { # Fallback if sign_index is somehow out of range
        "key": "unknown", "name": "Unknown", "symbol": "?",
        "longitude_ecliptic": round(ecliptic_longitude_degrees, 6),
        "longitude_normalized": round(lon_normalized, 6),
        "degrees_in_sign": 0.0, "display_short": "N/A", "display_dms": "N/A"
    }

def geocode_location_nominatim(location_query: str) -> Optional[Dict[str, Any]]:
    """
    Geocodes a location string to latitude, longitude, and Olson timezone
    using Nominatim (OpenStreetMap) and timezonefinder.
    User-Agent for Nominatim is fetched from app config.
    """
    if not location_query or not isinstance(location_query, str) or not location_query.strip():
        current_app.logger.warning("Geocoding attempted with empty or invalid location query.")
        return None

    if tf is None: # Check if TimezoneFinder initialized correctly
        current_app.logger.error("TimezoneFinder not initialized. Cannot geocode timezone.")
        return {"error": "Timezone lookup service is unavailable."}


    nominatim_url = "https://nominatim.openstreetmap.org/search"
    # Get User-Agent from Flask app config if available, otherwise use a default
    app_user_agent = current_app.config.get('APP_NAME_FOR_USER_AGENT', 'CosmicOracleApp/1.0 (Python Requests)')
    headers = {"User-Agent": app_user_agent}
    params = {"q": location_query, "format": "json", "limit": 1, "addressdetails": 1}

    try:
        response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)

        results = response.json()
        if results and isinstance(results, list) and len(results) > 0:
            top_result = results[0]
            lat_str = top_result.get("lat")
            lon_str = top_result.get("lon")
            display_name = top_result.get("display_name", "N/A")

            if lat_str is None or lon_str is None:
                current_app.logger.warning(f"Nominatim result for '{location_query}' missing lat/lon: {top_result}")
                return None

            latitude = float(lat_str)
            longitude = float(lon_str)

            if not (validate_latitude(latitude) and validate_longitude(longitude)):
                current_app.logger.warning(f"Invalid lat/lon from Nominatim for '{location_query}': lat={latitude}, lon={longitude}")
                return None

            timezone_name = tf.timezone_at(lng=longitude, lat=latitude) # Olson timezone
            if timezone_name is None:
                current_app.logger.warning(f"Could not determine timezone for lat={latitude}, lon={longitude} ({display_name}).")


            return {
                "query": location_query,
                "display_name": display_name,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone_name # Can be None if not found by timezonefinder
            }
        else:
            current_app.logger.info(f"No geocoding results found for query: '{location_query}'")
            return None
    except requests.exceptions.HTTPError as e:
        current_app.logger.error(f"Geocoding HTTP error for '{location_query}': {e.response.status_code} - {e.response.text}", exc_info=True)
        return {"error": f"Geocoding service error: {e.response.status_code}. Please try again later or refine your query."}
    except requests.exceptions.Timeout:
        current_app.logger.error(f"Geocoding request timed out for '{location_query}'.")
        return {"error": "Geocoding service timed out. Please try again later."}
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Geocoding general request error for '{location_query}': {e}", exc_info=True)
        return {"error": "Could not connect to geocoding service. Check internet connection or try again later."}
    except (ValueError, KeyError, IndexError, json.JSONDecodeError) as e: # More specific error handling for response processing
        current_app.logger.error(f"Error processing geocoding result for '{location_query}': {e}", exc_info=True)
        return {"error": "Error processing geocoding result. The service might be returning unexpected data."}