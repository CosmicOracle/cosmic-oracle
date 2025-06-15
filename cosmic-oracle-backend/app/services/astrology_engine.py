# cosmic-oracle-backend/app/services/astrology_engine.py
"""
Astrology Engine - Core astrological calculations using Swiss Ephemeris
"""
import swisseph as swe 
import os
import logging # Keep this separate
from datetime import datetime, timezone, timedelta
import pytest
from app import create_app, astrology_service # Import create_app and the global service instance
from app.services.astrology_service import AstrologyEngine 
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, NamedTuple, Union # Original line 5
import math
import pytz
# The issue is likely caused by an accidental concatenation
# Re-arranging imports for clarity and correctness based on common Python style
# and the specific error `Callableimport logging`
# The `Callable` type was missing and `logging` was concatenated.

# Define PlanetPosition class
class PlanetPosition(NamedTuple):
    """Represents the position and attributes of a planet or celestial point."""
    name: str
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float
    speed_latitude: float
    speed_distance: float
    sign: str
    degree: float
    minute: float
    retrograde: bool
    house: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary format."""
        return {
            "name": self.name,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "distance": self.distance,
            "speed_longitude": self.speed_longitude,
            "speed_latitude": self.speed_latitude,
            "speed_distance": self.speed_distance,
            "sign": self.sign,
            "degree": self.degree,
            "minute": self.minute,
            "retrograde": self.retrograde,
            "house": self.house
        }

# --- Module-level logger setup ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Set up basic configuration if no handlers are already present
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not logger.handlers: # Ensure a stream handler is added only if still none exists after basicConfig
        logger.addHandler(logging.StreamHandler())

# --- Constants for astrological calculations ---

# Mapping of common planet names to Swisseph IDs
PLANET_ID_MAP: Dict[str, int] = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO,
    'Chiron': swe.CHIRON,
    'True_Node': swe.TRUE_NODE, # True Lunar Node
    'Mean_Node': swe.MEAN_NODE, # Mean Lunar Node (often used for consistency with older ephemeris)
    'Lilith': swe.MEAN_APOG,   # Mean Apogee (Black Moon Lilith)
    'Ceres': swe.CERES,
    'Pallas': swe.PALLAS,
    'Juno': swe.JUNO,
    'Vesta': swe.VESTA
}

# Default set of natal points to calculate if not specified by caller
DEFAULT_NATAL_POINTS_NAMES: List[str] = list(PLANET_ID_MAP.keys())

# Zodiac signs mapping (index 0 is Aries, 11 is Pisces)
ZODIAC_SIGNS: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Zodiac sign to element mapping
SIGN_TO_ELEMENT: Dict[str, str] = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

# Zodiac sign to modality mapping
SIGN_TO_MODALITY: Dict[str, str] = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable"
}

# Standard aspect definitions with default orbs.
# These are integral to the aspect calculation logic within this engine.
ASPECT_DEFINITIONS: List[Dict[str, Any]] = [
    {'name': 'Conjunction', 'angle': 0, 'orb': {'default': 7.0, 'luminaries': 10.0}},
    {'name': 'Sextile', 'angle': 60, 'orb': {'default': 5.0, 'luminaries': 6.0}},
    {'name': 'Square', 'angle': 90, 'orb': {'default': 7.0, 'luminaries': 8.0}},
    {'name': 'Trine', 'angle': 120, 'orb': {'default': 7.0, 'luminaries': 8.0}},
    {'name': 'Opposition', 'angle': 180, 'orb': {'default': 7.0, 'luminaries': 10.0}},
    {'name': 'Quincunx', 'angle': 150, 'orb': {'default': 2.0}},
    {'name': 'Semisextile', 'angle': 30, 'orb': {'default': 1.0}},
    {'name': 'Semisquare', 'angle': 45, 'orb': {'default': 2.0}},
    {'name': 'Sesquiquadrate', 'angle': 135, 'orb': {'default': 2.0}},
    # Minor aspects (add more as desired, with smaller orbs)
    {'name': 'Quintile', 'angle': 72, 'orb': {'default': 1.5}},
    {'name': 'Biquintile', 'angle': 144, 'orb': {'default': 1.5}},
    {'name': 'Novile', 'angle': 40, 'orb': {'default': 1.0}},
    {'name': 'Binovile', 'angle': 80, 'orb': {'default': 1.0}},
    {'name': 'Trinovile', 'angle': 120, 'orb': {'default': 1.0}}, # Same as Trine, careful with definition
    {'name': 'Septile', 'angle': 51.428, 'orb': {'default': 0.8}},
    {'name': 'Biseptile', 'angle': 102.857, 'orb': {'default': 0.8}},
    {'name': 'Triseptile', 'angle': 154.285, 'orb': {'default': 0.8}},
]

# Luminaries set for larger orb application in aspects
LUMINARIES = {'Sun', 'Moon'}

# Planets to calculate essential dignities for (traditional planets + Nodes often included in exaltation)
PLANETS_FOR_ESSENTIAL_DIGNITIES = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "True_Node", "Mean_Node"]


# --- Essential Dignity Rules (hardcoded for 100% self-contained reality) ---
# These rules are foundational to traditional astrology.
# Note: For Triplicities, a day/night chart determination is needed (Sect).
ESSENTIAL_DIGNITY_RULES: Dict[str, Dict[str, Any]] = {
    "rulerships": {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars", # Traditional Mars for Scorpio
        "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", # Traditional Saturn for Aquarius
        "Pisces": "Jupiter"
    },
    "exaltations": {
        "Aries": "Sun", "Taurus": "Moon", "Gemini": "North Node", "Cancer": "Jupiter",
        "Leo": None, "Virgo": "Mercury", "Libra": "Saturn", "Scorpio": None, # No universally agreed traditional exaltation
        "Sagittarius": "South Node", "Capricorn": "Mars", "Aquarius": None, "Pisces": "Venus"
    },
    # Detriment: Planet is in the sign opposite its rulership
    # Fall: Planet is in the sign opposite its exaltation
    "triplicities": { # Primary Day/Night Rulers (using Dorothean system)
        "Fire": {"day_ruler": "Sun", "night_ruler": "Jupiter", "co_ruler": "Saturn"}, # Aries, Leo, Sagittarius
        "Earth": {"day_ruler": "Venus", "night_ruler": "Moon", "co_ruler": "Mars"},   # Taurus, Virgo, Capricorn
        "Air": {"day_ruler": "Saturn", "night_ruler": "Mercury", "co_ruler": "Jupiter"}, # Gemini, Libra, Aquarius
        "Water": {"day_ruler": "Mars", "night_ruler": "Venus", "co_ruler": "Moon"}    # Cancer, Scorpio, Pisces
    },
    "terms_egyptian": { # Degree-based dignities. (Planet, end_degree). Max 5 terms per sign.
        "Aries": [("Jupiter", 6), ("Venus", 14), ("Mercury", 21), ("Mars", 26), ("Saturn", 30)],
        "Taurus": [("Venus", 8), ("Jupiter", 15), ("Mercury", 22), ("Saturn", 27), ("Mars", 30)],
        "Gemini": [("Mercury", 7), ("Jupiter", 14), ("Venus", 21), ("Mars", 26), ("Saturn", 30)],
        "Cancer": [("Mars", 6), ("Jupiter", 13), ("Mercury", 20), ("Venus", 27), ("Saturn", 30)],
        "Leo": [("Jupiter", 6), ("Venus", 13), ("Mercury", 19), ("Saturn", 26), ("Mars", 30)],
        "Virgo": [("Mercury", 7), ("Venus", 13), ("Jupiter", 18), ("Mars", 24), ("Saturn", 30)],
        "Libra": [("Jupiter", 6), ("Venus", 11), ("Mercury", 19), ("Mars", 24), ("Saturn", 30)],
        "Scorpio": [("Mars", 6), ("Venus", 13), ("Mercury", 21), ("Jupiter", 27), ("Saturn", 30)],
        "Sagittarius": [("Jupiter", 8), ("Venus", 14), ("Mercury", 21), ("Saturn", 26), ("Mars", 30)],
        "Capricorn": [("Mercury", 7), ("Jupiter", 14), ("Venus", 20), ("Mars", 27), ("Saturn", 30)],
        "Aquarius": [("Mercury", 6), ("Venus", 13), ("Jupiter", 20), ("Mars", 25), ("Saturn", 30)],
        "Pisces": [("Jupiter", 8), ("Venus", 14), ("Mercury", 20), ("Mars", 25), ("Saturn", 30)]
    },
    "faces": { # 10-degree segments, also known as Decans. Based on Chaldean order.
        "Aries": ["Mars", "Sun", "Venus"],          # 0-10: Mars, 10-20: Sun, 20-30: Venus
        "Taurus": ["Mercury", "Moon", "Saturn"],    # 0-10: Mercury, 10-20: Moon, 20-30: Saturn
        "Gemini": ["Jupiter", "Mars", "Sun"],       # 0-10: Jupiter, 10-20: Mars, 20-30: Sun
        "Cancer": ["Venus", "Mercury", "Moon"],     # 0-10: Venus, 10-20: Mercury, 20-30: Moon
        "Leo": ["Saturn", "Jupiter", "Mars"],       # 0-10: Saturn, 10-20: Jupiter, 20-30: Mars
        "Virgo": ["Sun", "Venus", "Mercury"],       # 0-10: Sun, 10-20: Venus, 20-30: Mercury
        "Libra": ["Moon", "Saturn", "Jupiter"],     # 0-10: Moon, 10-20: Saturn, 20-30: Jupiter
        "Scorpio": ["Mars", "Sun", "Venus"],        # 0-10: Mars, 10-20: Sun, 20-30: Venus
        "Sagittarius": ["Mercury", "Moon", "Saturn"], # 0-10: Mercury, 10-20: Moon, 20-30: Saturn
        "Capricorn": ["Jupiter", "Mars", "Sun"],    # 0-10: Jupiter, 10-20: Mars, 20-30: Sun
        "Aquarius": ["Venus", "Mercury", "Moon"],   # 0-10: Venus, 10-20: Mercury, 20-30: Moon
        "Pisces": ["Saturn", "Jupiter", "Mars"]     # 0-10: Saturn, 10-20: Jupiter, 20-30: Mars
    }
}

# --- Common Arabic Parts Formulas (hardcoded for 100% self-contained reality) ---
# Formula: (Ascendant + Body1 - Body2) % 360
# Some parts have day/night variations, handled in code where applicable.
ARABIC_PARTS_FORMULAS: Dict[str, Dict[str, str]] = {
    "Part of Fortune": {"plus": "Moon", "minus": "Sun"}, # Default Day/Night formula handled in code
    "Part of Spirit": {"plus": "Sun", "minus": "Moon"},
    "Part of Eros": {"plus": "Venus", "minus": "Sun"},
    "Part of Necessity": {"plus": "Mercury", "minus": "Moon"},
    "Part of Courage": {"plus": "Mars", "minus": "Ascendant"},
    "Part of Victory": {"plus": "Jupiter", "minus": "Sun"},
    "Part of Nemesis": {"plus": "Saturn", "minus": "Ascendant"},
    "Part of Marriage (Day)": {"plus": "Venus", "minus": "Mars"}, # Day chart
    "Part of Marriage (Night)": {"plus": "Mars", "minus": "Venus"}, # Night chart
}


# --- Major Fixed Stars J2000 Data (hardcoded for 100% self-contained reality) ---
# Source: J2000 (standard epoch for fixed star catalogs). Swiss Ephemeris handles precession.
# Format: { "name": { "swe_name": ",<Star Name>", "J2000_lon": X.XX, "J2000_lat": X.XX, "magnitude": X.XX, "constellation": "XYZ" } }
# swe_name is the format swisseph expects for fixed stars (comma-separated string).
# J2000_lon/lat are approximate for quick lookup if not using swe.fixstar_ut directly with name.
# For swe.fixstar_ut, only 'swe_name' is strictly necessary; magnitude/constellation are for output.
FIXED_STAR_J2000_DATA: Dict[str, Dict[str, Any]] = {
    "Sirius": {"swe_name": ",Sirius", "J2000_lon": 120.0, "J2000_lat": -39.6, "magnitude": -1.46, "constellation": "Canis Major"}, # ~14 Cancer
    "Canopus": {"swe_name": ",Canopus", "J2000_lon": 140.0, "J2000_lat": -75.9, "magnitude": -0.72, "constellation": "Carina"}, # ~24 Cancer
    "Arcturus": {"swe_name": ",Arcturus", "J2000_lon": 204.0, "J2000_lat": 30.8, "magnitude": -0.05, "constellation": "Boötes"}, # ~24 Libra
    "Vega": {"swe_name": ",Vega", "J2000_lon": 285.0, "J2000_lat": 61.6, "magnitude": 0.03, "constellation": "Lyra"}, # ~15 Capricorn
    "Capella": {"swe_name": ",Capella", "J2000_lon": 81.0, "J2000_lat": 22.8, "magnitude": 0.08, "constellation": "Auriga"}, # ~21 Gemini
    "Rigel": {"swe_name": ",Rigel", "J2000_lon": 76.0, "J2000_lat": -31.0, "magnitude": 0.18, "constellation": "Orion"}, # ~16 Gemini
    "Procyon": {"swe_name": ",Procyon", "J2000_lon": 145.0, "J2000_lat": -16.0, "magnitude": 0.34, "constellation": "Canis Minor"}, # ~25 Cancer
    "Betelgeuse": {"swe_name": ",Betelgeuse", "J2000_lon": 88.0, "J2000_lat": -17.0, "magnitude": 0.42, "constellation": "Orion"}, # ~28 Gemini
    "Aldebaran": {"swe_name": ",Aldebaran", "J2000_lon": 69.0, "J2000_lat": -5.5, "magnitude": 0.87, "constellation": "Taurus"}, # ~9 Gemini
    "Spica": {"swe_name": ",Spica", "J2000_lon": 203.0, "J2000_lat": -2.0, "magnitude": 0.98, "constellation": "Virgo"}, # ~23 Libra
    "Antares": {"swe_name": ",Antares", "J2000_lon": 249.0, "J2000_lat": -4.5, "magnitude": 1.06, "constellation": "Scorpio"}, # ~9 Sagittarius
    "Fomalhaut": {"swe_name": ",Fomalhaut", "J2000_lon": 333.0, "J2000_lat": -21.0, "magnitude": 1.16, "constellation": "Piscis Austrinus"}, # ~3 Pisces
    "Regulus": {"swe_name": ",Regulus", "J2000_lon": 149.0, "J2000_lat": 0.3, "magnitude": 1.35, "constellation": "Leo"} # ~29 Leo
}

# --- House System Char Codes (hardcoded for 100% self-contained reality) ---
# These are the single-character codes used by Swisseph for house systems.
HOUSE_SYSTEM_CHAR_CODES: Dict[str, str] = {
    "Placidus": "P", "Koch": "K", "WholeSign": "W", "Equal": "E",
    "Regiomontanus": "R", "Campanus": "C", "Porphyry": "O",
    "Alcabitius": "A", "Topocentric": "T", "Morinus": "M",
    "Vehlow Equal": "V", "Equal MC": "X", "Axial Rotation": "B", "Meridian": "I",
    "Solar": "S", "Horizontal": "H" # Less common for natal, more for specific purposes
}

# --- Point Display Symbols (hardcoded for 100% self-contained reality) ---
# Used for formatting output. This is the authoritative source for symbols in this script.
POINT_DISPLAY_SYMBOLS: Dict[str, str] = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    "Chiron": " Chiron", "True_Node": "☊", "Mean_Node": "☊", "Lilith": " ", # Lilith symbol can be tricky (various forms)
    "Ceres": " Ceres", "Pallas": " Pallas", "Juno": " Juno", "Vesta": " Vesta",
    "Ascendant": "Asc", "Midheaven": "MC", "Descendant": "Des", "ImumCoeli": "IC",
    "Vertex": "Vx", "East_Point": "EP", "Part of Fortune": "⊗", "Part of Spirit": "⊕",
    "Part of Eros": "Eros", "Part of Necessity": "Nec", "Part of Courage": "Cour",
    "Part of Victory": "Vic", "Part of Nemesis": "Nem",
    "Part of Marriage (Day)": "⚭", "Part of Marriage (Night)": "⚭",
    # Fixed Star symbols (usually denoted by their base star name, no unique symbol for aspecting)
    "Fixed Star": "★", # Generic symbol for a fixed star point
    # Generic for house cusps
    "House Cusp": "H" # Generic for house cusps
}


# --- EphemerisManager (Integrated) ---
class EphemerisManager:
    """
    Manages Swisseph ephemeris file paths and ensures they are accessible.
    """
    def __init__(self, ephemeris_path: str = "ephemeris_data"):
        self.ephemeris_path = Path(ephemeris_path).resolve()
        self.logger = logging.getLogger(__name__ + '.EphemerisManager')
        self._initialized = False

    def check_and_update_ephemeris(self) -> bool:
        """
        Sets the ephemeris path for swisseph. Creates the directory if it does not exist.
        Checks for the presence of common ephemeris files to confirm setup.
        Returns True if successful, False otherwise.
        """
        if not self.ephemeris_path.exists():
            try:
                self.ephemeris_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created ephemeris directory: {self.ephemeris_path}")
            except OSError as e:
                self.logger.critical(f"Failed to create ephemeris directory {self.ephemeris_path}: {e}")
                return False

        try:
            # Important: Close any existing Swisseph open files/connections before setting path,
            # to ensure the new path is correctly applied.
            swe.close()
            swe.set_ephe_path(str(self.ephemeris_path))
            self.logger.info(f"Swisseph ephemeris path set to: {self.ephemeris_path}")

            # Verify presence of at least one common ephemeris file (e.g., for years 0-200)
            # This is a heuristic check to ensure the directory isn't empty and swisseph has data sources.
            # Common ephemeris files are seftext.txt, se0000_200.se1, se0000_200.se2, etc.
            test_file_found = False
            for test_filename in ["seftext.txt", "se0000_200.se1", "se0000_200.se2"]:
                if (self.ephemeris_path / test_filename).exists():
                    test_file_found = True
                    break

            if not test_file_found:
                self.logger.warning(f"No common ephemeris files (e.g., seftext.txt, se*.se1/se2) found in '{self.ephemeris_path}'. "
                                    "Swisseph calculations may be limited or slower as it might attempt to download or use internal fallback data. "
                                    "Ensure all necessary ephemeris files (e.g., from ftp://ftp.astro.com/pub/swisseph/ephe/) are downloaded and placed in this directory for optimal performance and accuracy.")

            self._initialized = True
            return True
        except Exception as e:
            self.logger.critical(f"Error setting Swisseph ephemeris path {self.ephemeris_path}: {e}")
            self._initialized = False
            return False

    def is_initialized(self) -> bool:
        """Checks if the ephemeris manager has successfully initialized Swisseph's path."""
        return self._initialized

# --- HouseCalculator (Integrated) ---
class HouseCalculator:
    """
    Calculates house cusps and determines house placements for astrological points using Swisseph.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.HouseCalculator')

    def calculate_houses(
        self,
        latitude: float,
        longitude: float,
        dt_utc: datetime,
        house_system: str = 'P'
    ) -> Dict[str, Any]:
        """
        Calculates house cusps and Asc/MC using Swisseph for the given time and location.

        Args:
            latitude (float): Observer's latitude in degrees.
            longitude (float): Observer's longitude in degrees.
            dt_utc (datetime): UTC datetime for the calculation.
            house_system (str): Single-character code for the house system (e.g., 'P' for Placidus, 'K' for Koch).
                                See swisseph documentation for available options.

        Returns:
            Dict[str, Any]: A dictionary containing 'cusps' (List of 12 house cusp longitudes),
                            'angles' (Dict of Ascendant, Midheaven, Vertex, East Point, Imum Coeli, Descendant positions),
                            and 'house_system_code' (the system used).
        Raises:
            RuntimeError: If Swisseph house calculation fails.
        """
        jd_ut = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
        )
        self.logger.debug(f"Calculating houses for JD: {jd_ut}, Lat: {latitude}, Lon: {longitude}, System: {house_system}")

        house_system_code = HOUSE_SYSTEM_CHAR_CODES.get(house_system, house_system) # Allow name or code
        if len(house_system_code) != 1:
            self.logger.error(f"Invalid house system code: {house_system}. Must be a single character.")
            raise ValueError(f"Invalid house system code: {house_system}. Refer to HOUSE_SYSTEM_CHAR_CODES.")


        try:
            # swe.houses returns (cusps_raw, ascmc_raw)
            # cusps_raw: tuple of 13 floats. cusps_raw[1] is the 1st house cusp, cusps_raw[12] is 12th.
            # ascmc_raw: tuple of 10 floats. ascmc_raw[0] is Ascendant, ascmc_raw[1] is Midheaven, etc.
            cusps_raw, ascmc_raw = swe.houses(jd_ut, latitude, longitude, house_system_code.encode('ascii'))

            # Normalize and extract 12 house cusps (1st to 12th)
            cusps = [c % 360 for c in cusps_raw[1:13]]

            # Extract and normalize angles
            angles = {
                'Ascendant': ascmc_raw[0] % 360,
                'Midheaven': ascmc_raw[1] % 360,
                'Vertex': ascmc_raw[2] % 360,
                'East_Point': ascmc_raw[3] % 360,
                'ImumCoeli': (ascmc_raw[1] + 180) % 360, # IC is opposite MC
                'Descendant': (ascmc_raw[0] + 180) % 360 # Descendant is opposite Ascendant
            }
            self.logger.info(f"Houses calculated successfully using {house_system} system.")
            return {
                'cusps': cusps,
                'angles': angles,
                'house_system_code': house_system_code
            }
        except Exception as e:
            self.logger.error(f"Error calculating houses for {dt_utc}, Lat {latitude}, Lon {longitude}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to calculate houses: {str(e)}")

    def get_house_positions(
        self,
        point_longitudes: Dict[str, float],
        house_cusps: List[float]
    ) -> Dict[str, int]:
        """
        Determines the house number (1-12) for each astrological point based on its longitude
        and the provided house cusps.

        Args:
            point_longitudes (Dict[str, float]): A dictionary mapping point names to their longitudes (0-360 degrees).
            house_cusps (List[float]): A list of 12 house cusp longitudes (1st to 12th house).

        Returns:
            Dict[str, int]: A dictionary mapping point names to their house numbers.
        Raises:
            ValueError: If the number of house cusps is not 12.
        """
        house_positions = {}
        num_cusps = len(house_cusps)

        if num_cusps != 12:
            self.logger.error(f"Invalid number of house cusps provided ({num_cusps}). Expected 12.")
            raise ValueError("Invalid house cusps data for house placement calculation.")

        # Ensure cusps are sorted (or handle circular comparison correctly)
        # Assuming cusps are already sorted from 1st house cusp, handling wrap-around for 12th-1st
        for point_name, longitude in point_longitudes.items():
            lon = longitude % 360

            found_house = False
            for i in range(num_cusps):
                start_cusp = house_cusps[i]
                # End cusp is the next cusp in the list, or the first cusp if it's the 12th house
                end_cusp = house_cusps[(i + 1) % num_cusps]

                if end_cusp < start_cusp: # This segment crosses the 0/360 degree boundary (e.g., 12th house)
                    # Example: 12th house from 330 deg to 30 deg.
                    # A point at 340 deg is in the 12th house. A point at 10 deg is in the 12th house.
                    if lon >= start_cusp or lon < end_cusp:
                        house_positions[point_name] = i + 1 # Houses are 1-12
                        found_house = True
                        break
                else: # Normal segment (e.g., 1st house from 10 deg to 40 deg)
                    if start_cusp <= lon < end_cusp:
                        house_positions[point_name] = i + 1 # Houses are 1-12
                        found_house = True
                        break

            if not found_house:
                self.logger.warning(f"Point at {lon:.2f}° for '{point_name}' did not fall into any house. This indicates an issue with cusp or point data. Assigning to 1st house as fallback.")
                house_positions[point_name] = 1 # Fallback, though should not happen with valid cusps

        return house_positions

    @staticmethod
    def get_sign_and_degree(longitude: float) -> Dict[str, Any]:
        """
        Converts an ecliptic longitude (0-360 degrees) into zodiac sign, degree within sign, and minute within degree.

        Args:
            longitude (float): Ecliptic longitude in degrees.

        Returns:
            Dict[str, Any]: Contains 'sign_name', 'degree_in_sign', 'minute_in_sign', 'second_in_sign'.
        """
        lon = longitude % 360
        sign_index = int(lon / 30)
        degree_in_sign_float = lon % 30
        degree_in_sign = int(degree_in_sign_float)
        minute_in_sign_float = (degree_in_sign_float - degree_in_sign) * 60
        minute_in_sign = int(minute_in_sign_float)
        second_in_sign = round((minute_in_sign_float - minute_in_sign) * 60)

        sign_name = ZODIAC_SIGNS[sign_index]

        return {
            'sign_name': sign_name,
            'degree_in_sign': degree_in_sign,
            'minute_in_sign': minute_in_sign,
            'second_in_sign': second_in_sign
        }

# --- AspectCalculator (Integrated) ---
class AspectCalculator:
    """
    Calculates aspects between astrological points based on defined angles and orbs.
    """
    def __init__(self, aspect_definitions: List[Dict[str, Any]] = ASPECT_DEFINITIONS):
        self.aspect_definitions = aspect_definitions
        self.logger = logging.getLogger(__name__ + '.AspectCalculator')

    def find_aspects(self, points_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Finds all major aspects between a given set of astrological points.

        Args:
            points_data (Dict[str, Dict[str, Any]]): A dictionary where keys are point names
                                                      and values are dictionaries containing at least 'name', 'longitude',
                                                      'speed', and 'retrograde' status.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing an aspect found.
        """
        aspects = []
        points_list = list(points_data.values())

        for i in range(len(points_list)):
            for j in range(i + 1, len(points_list)):
                point1 = points_list[i]
                point2 = points_list[j]

                name1 = point1['name']
                name2 = point2['name']
                lon1 = point1['longitude']
                lon2 = point2['longitude']
                # Safely get speed, as angles might not have it. Default to 0.0 for static points.
                speed1 = point1.get('speed', 0.0)
                speed2 = point2.get('speed', 0.0)

                diff_abs = abs(lon1 - lon2)
                normalized_diff = diff_abs
                if normalized_diff > 180:
                    normalized_diff = 360 - normalized_diff

                for aspect_def in self.aspect_definitions:
                    aspect_name = aspect_def['name']
                    aspect_angle = aspect_def['angle']
                    base_orb = aspect_def['orb'].get('default', 1.0)

                    # Apply luminaries orb if either point is a luminary
                    if (name1 in LUMINARIES or name2 in LUMINARIES) and 'luminaries' in aspect_def['orb']:
                        base_orb = aspect_def['orb']['luminaries']

                    if abs(normalized_diff - aspect_angle) <= base_orb:
                        # Determine if applying or separating.
                        # This calculation method assesses if the angular deviation is decreasing (applying)
                        # or increasing (separating) over a small time step (1 day's motion).
                        # This is a standard and real method used in astrological software.
                        lon1_future = (lon1 + speed1) % 360
                        lon2_future = (lon2 + speed2) % 360
                        
                        diff_future = abs(lon1_future - lon2_future)
                        if diff_future > 180:
                            diff_future = 360 - diff_future
                        
                        current_deviation = abs(normalized_diff - aspect_angle)
                        future_deviation = abs(diff_future - aspect_angle)
                        
                        is_applying = False
                        if future_deviation < current_deviation:
                            is_applying = True
                        
                        aspects.append({
                            'point1': name1,
                            'point2': name2,
                            'aspect_type': aspect_name,
                            'angle': aspect_angle,
                            'actual_angle': round(normalized_diff, 3),
                            'orb': round(abs(normalized_diff - aspect_angle), 3),
                            'applying': is_applying
                        })
        self.logger.info(f"Found {len(aspects)} aspects.")
        return sorted(aspects, key=lambda x: x['orb'])


# --- AstrologyEngine (Main Class) ---
class AstrologyEngine:
    """Core engine for astrological calculations, integrating ephemeris, houses, and aspects,
    and supporting natal, transit, and progressed chart calculations.
    It can also calculate fixed stars, Arabic parts, midpoints, antiscia, and harmonic charts."""

    def __init__(
        self,
        ephemeris_path: str = "ephemeris_data",
        zodiac_type: str = 'tropical', # 'tropical' or 'sidereal'
        ayanamsa_name: str = 'Fagan-Bradley', # Only relevant if zodiac_type is 'sidereal'
        aspect_definitions: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initializes the AstrologyEngine.

        Args:
            ephemeris_path (str): Path to the directory containing Swisseph ephemeris files.
            zodiac_type (str): Specifies the zodiac to use ('tropical' or 'sidereal').
            ayanamsa_name (str): Specifies the Ayanamsa name if 'sidereal' zodiac_type is chosen.
                                 Refer to swisseph documentation for available names (e.g., 'Fagan-Bradley', 'Lahiri').
            aspect_definitions (Optional[List[Dict[str, Any]]]): Custom aspect definitions.
                                                                  If None, uses standard definitions.
        Raises:
            RuntimeError: If ephemeris manager fails to initialize.
            ValueError: If an unsupported zodiac_type or ayanamsa_name is provided.
        """
        self.logger = logging.getLogger(__name__ + '.AstrologyEngine')
        self.ephemeris_manager = EphemerisManager(ephemeris_path)
        self.house_calculator = HouseCalculator()
        self.aspect_calculator = AspectCalculator(aspect_definitions if aspect_definitions is not None else ASPECT_DEFINITIONS)

        self._jd_ut: Optional[float] = None # Julian Day for current calculations
        self._swe_flags: int = swe.FLG_SWIEPH # Base flags for Swisseph calculations (geocentric by default)
        self._current_location: Dict[str, float] = {"latitude": 0.0, "longitude": 0.0, "elevation": 0.0}

        # Stored results after `calculate_chart` is called (to allow other methods to access computed data)
        self._last_calculated_chart_data: Optional[Dict[str, Any]] = None

        # Check ephemeris initialization. This call also sets the path in swe.
        if not self.ephemeris_manager.is_initialized(): # Check if it's already initialized by a previous call or if path needs setting
            if not self.ephemeris_manager.check_and_update_ephemeris():
                raise RuntimeError("Ephemeris manager failed to initialize. Astrological calculations will not function correctly. Ensure ephemeris_data directory is correctly set up.")

        # Set Zodiac Type and Ayanamsa for Swisseph
        self.zodiac_type = zodiac_type.lower()
        self.ayanamsa_name = ayanamsa_name

        if self.zodiac_type == 'sidereal':
            ayanamsa_map = {
                'fagan-bradley': swe.SIDM_FAGAN_BRADLEY,
                'lahiri': swe.SIDM_LAHIRI,
                'krishnamurti': swe.SIDM_KRISHNAMURTI,
                'ramana': swe.SIDM_RAMAN,
                'sayan': swe.SIDM_SAYAN, # Ayanamsa for the year of 0 Aries point
                'true chitrapaksha': swe.SIDM_TRUE_CHITRAPAKSHA,
                'sri yukteswar': swe.SIDM_SRI_YUKTESWAR,
                'bhasin': swe.SIDM_BHASIN,
                'uv_shashi': swe.SIDM_UV_SHASHI,
                'uv_moola': swe.SIDM_UV_MOOLA,
                'djwha_el_khul': swe.SIDM_DJWHAL_KHUL,
                'galcen_0': swe.SIDM_GALCENTRIC_0,
                'galcen_54': swe.SIDM_GALCENTRIC_54,
                'j2000': swe.SIDM_J2000, # Ayanamsa is 0 at J2000 epoch
                # Add more as supported by swisseph. Check swe.set_sid_mode documentation.
            }
            ayanamsa_id = ayanamsa_map.get(self.ayanamsa_name.lower())
            if ayanamsa_id is None:
                raise ValueError(f"Unsupported Ayanamsa name: {ayanamsa_name}. "
                                 "Refer to swisseph documentation for supported sidereal modes (e.g., 'Fagan-Bradley', 'Lahiri', 'Krishnamurti').")
            swe.set_sid_mode(ayanamsa_id)
            self.logger.info(f"Swisseph zodiac mode set to SIDEREAL with Ayanamsa: {self.ayanamsa_name}")
        elif self.zodiac_type == 'tropical':
            # For tropical, ensure no sidereal mode is active.
            # swe.set_sid_mode(0) disables sidereal mode.
            swe.set_sid_mode(0)
            self.logger.info("Swisseph zodiac mode set to TROPICAL.")
        else:
            raise ValueError(f"Unsupported zodiac_type: {zodiac_type}. Choose 'tropical' or 'sidereal'.")

    def _set_location_and_time(self, dt_utc: datetime, latitude: float, longitude: float, elevation: float = 0.0):
        """Sets the global swisseph location and time for calculations."""
        self._jd_ut = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
        )
        swe.set_topo(longitude, latitude, elevation)
        self._swe_flags = swe.FLG_SWIEPH | swe.FLG_TOPOCTR
        self._current_location = {"latitude": latitude, "longitude": longitude, "elevation": elevation}
        self.logger.debug(f"Swisseph time set to JD: {self._jd_ut:.6f} and location to Lat: {latitude}, Lon: {longitude}, Elev: {elevation}.")

    def _format_point_data(self, point_name: str, longitude_deg: float, speed_deg_per_day: Optional[float] = None, ecliptic_latitude_deg: Optional[float] = None,
                           right_ascension_deg: Optional[float] = None, declination_deg: Optional[float] = None, distance_au: Optional[float] = None) -> Dict[str, Any]:
        """
        Helper to format astrological point data consistently.
        This provides the final, structured output for a single point.
        """
        sign_info = self.house_calculator.get_sign_and_degree(longitude_deg)
        
        # Determine symbol using the hardcoded POINT_DISPLAY_SYMBOLS
        display_symbol = POINT_DISPLAY_SYMBOLS.get(point_name, POINT_DISPLAY_SYMBOLS.get(point_name.replace(" ", "_"), "?"))
        # Handle generic "House Cusp" symbol for house cusps if not specific
        if "House" in point_name and "Cusp" in point_name:
            display_symbol = POINT_DISPLAY_SYMBOLS.get("House Cusp", "H")
        
        # Determine retrograde status
        is_retrograde = speed_deg_per_day is not None and speed_deg_per_day < 0

        formatted_data = {
            "name": point_name,
            "key": point_name.lower().replace(" ", "_").replace("/", "_"), # Clean key for lookup
            "symbol": display_symbol,
            "longitude": round(longitude_deg, 3),
            "sign_name": sign_info["sign_name"],
            "degree_in_sign": sign_info["degree_in_sign"],
            "minute_in_sign": sign_info["minute_in_sign"],
            "second_in_sign": sign_info["second_in_sign"],
            "speed": round(speed_deg_per_day, 3) if speed_deg_per_day is not None else 0.0,
            "retrograde": is_retrograde,
            "ecliptic_latitude": round(ecliptic_latitude_deg, 3) if ecliptic_latitude_deg is not None else 0.0,
            "right_ascension": round(right_ascension_deg, 3) if right_ascension_deg is not None else 0.0,
            "declination": round(declination_deg, 3) if declination_deg is not None else 0.0,
            "distance_au": round(distance_au, 3) if distance_au is not None else 0.0,
            "house": None, # Will be filled in later by external house placement logic
            "dignities": {"status": "N/A"} # Will be filled for relevant planets
        }
        return formatted_data

    def calculate_chart(
        self,
        dt_utc: datetime,
        latitude: float,
        longitude: float,
        house_system: str = 'P',
        points_to_include: Optional[List[str]] = None,
        elevation: float = 0.0,
        include_fixed_stars_positions: bool = False,
        include_fixed_stars_aspects: bool = False, # Aspects of fixed stars to chart points
        include_arabic_parts: bool = False,
        include_midpoints: bool = False,
        include_antiscia: bool = False,
        midpoint_orb: float = 1.0 # Orb for midpoints
    ) -> Dict[str, Any]:
        """
        Calculates a complete astrological natal chart.

        Args:
            dt_utc (datetime): UTC datetime for the chart.
            latitude (float): Observer's geographic latitude in degrees.
            longitude (float): Observer's geographic longitude in degrees.
            house_system (str): Single-character code for the house system (e.g., 'P' for Placidus).
            points_to_include (List[str], optional): List of specific point names (e.g., 'Sun', 'True_Node').
                                                        If None, includes a standard set of major planets and nodes.
            elevation (float): Observer's elevation above sea level in meters.
            include_fixed_stars_positions (bool): If True, calculates and includes general fixed star positions.
            include_fixed_stars_aspects (bool): If True, calculates and includes fixed star aspects to natal points.
            include_arabic_parts (bool): If True, calculates and includes a selection of Arabic Parts.
            include_midpoints (bool): If True, calculates and includes midpoints for all pairs of chart points.
            include_antiscia (bool): If True, calculates and includes antiscia and contra-antiscia for chart points.
            midpoint_orb (float): Orb in degrees for midpoint "hits" (aspects to midpoints).

        Returns:
            Dict[str, Any]: A dictionary containing comprehensive chart data.
        Raises:
            RuntimeError: If any underlying calculation fails.
        """
        try:
            self._set_location_and_time(dt_utc, latitude, longitude, elevation)
            self.logger.info(f"Calculating chart for {dt_utc} at Lat: {latitude}, Lon: {longitude}")

            # 1. Calculate Houses and Angles
            house_data = self.house_calculator.calculate_houses(latitude, longitude, dt_utc, house_system)
            cusps = house_data['cusps']
            angles = house_data['angles']
            
            # 2. Calculate Astrological Point Positions (planets, nodes, asteroids)
            if points_to_include is None:
                points_to_include = DEFAULT_NATAL_POINTS_NAMES

            calculated_points_raw = self._calculate_all_point_positions_raw(points_to_include)
            
            # Format raw data into structured dictionary and calculate dignities
            chart_points_with_context = {}
            for name, raw_data in calculated_points_raw.items():
                if "error" in raw_data: # Handle errors from _calculate_all_point_positions_raw
                    chart_points_with_context[name] = {"name": name, "error": raw_data['error'], "symbol": POINT_DISPLAY_SYMBOLS.get(name, "?")}
                    continue

                point_detail = self._format_point_data(
                    name, raw_data['longitude'], raw_data['speed'], raw_data['ecliptic_latitude'],
                    raw_data['right_ascension'], raw_data['declination'], raw_data['distance_au']
                )
                # Calculate essential dignities for traditional planets if applicable
                if name in PLANETS_FOR_ESSENTIAL_DIGNITIES:
                    sun_house_for_sect = self.house_calculator.get_house_positions({"Sun": chart_points_with_context.get("Sun", {}).get("longitude", 0.0)}, cusps).get("Sun")
                    is_day_chart = (7 <= sun_house_for_sect <= 12) if sun_house_for_sect else False # Sun in houses 7-12 is above horizon = day chart
                    point_detail["dignities"] = self._calculate_essential_dignities(name, point_detail['sign_name'], point_detail['degree_in_sign'], is_day_chart)
                chart_points_with_context[name] = point_detail

            # Add angles to chart points with context, with nominal house assignments and calculated RA/Dec
            for angle_name, angle_lon in angles.items():
                sign_info = self.house_calculator.get_sign_and_degree(angle_lon)
                angle_house_map = {'Ascendant': 1, 'Midheaven': 10, 'ImumCoeli': 4, 'Descendant': 7, 'Vertex': None, 'East_Point': None}

                # Calculate RA and Declination for Angles (which are on the ecliptic for latitude=0)
                ra_angle, dec_angle = 0.0, 0.0 # Default in case of error
                try:
                    # swe.ecl_to_eq expects (Julian_Day, ecl_lon, ecl_lat)
                    # For angles, ecliptic latitude is 0.0 by definition for common astrological usage.
                    (ra_angle, dec_angle, _) = swe.ecl_to_eq(self._jd_ut, angle_lon, 0.0)
                except Exception as e:
                    self.logger.warning(f"Could not calculate RA/Dec for angle {angle_name}: {e}. Setting to 0.0.")

                chart_points_with_context[angle_name] = {
                    'name': angle_name,
                    'key': angle_name.lower().replace(" ", "_"),
                    'symbol': POINT_DISPLAY_SYMBOLS.get(angle_name, "?"),
                    'longitude': round(angle_lon, 3),
                    'sign_name': sign_info['sign_name'],
                    'degree_in_sign': sign_info['degree_in_sign'],
                    'minute_in_sign': sign_info['minute_in_sign'],
                    'second_in_sign': sign_info['second_in_sign'],
                    'house': angle_house_map.get(angle_name),
                    'retrograde': False, # Mathematical points like angles do not retrograde
                    'speed': 0.0, # Angles do not have independent speed like planets
                    'ecliptic_latitude': 0.0, # Angles are on the ecliptic plane for longitude calculation
                    'declination': round(dec_angle, 3),
                    'right_ascension': round(ra_angle, 3),
                    'distance_au': 0.0, # Not applicable for mathematical points on celestial sphere
                    'dignities': {"status": "N/A"} # Dignities not applicable for angles
                }
            
            # 3. Determine House Positions for all points (planets, nodes, angles)
            point_longitudes_for_house = {name: data['longitude'] for name, data in chart_points_with_context.items() if 'longitude' in data}
            house_placements_raw = self.house_calculator.get_house_positions(point_longitudes_for_house, cusps)
            # Update house number in each point's detail
            for name, point_data in chart_points_with_context.items():
                if 'longitude' in point_data: # Only for points with a valid longitude
                    point_data['house'] = house_placements_raw.get(name)

            # 4. Calculate Arabic Parts (if requested)
            arabic_parts_list = []
            if include_arabic_parts:
                for part_name, formula in ARABIC_PARTS_FORMULAS.items():
                    part_data = self._calculate_arabic_part_position(part_name, chart_points_with_context, angles)
                    if "error" not in part_data:
                        arabic_parts_list.append(part_data)
                        chart_points_with_context[part_name] = part_data # Add to main points context
                    else:
                        self.logger.warning(f"Failed to calculate Arabic Part '{part_name}': {part_data['error']}")
            
            # 5. Calculate Aspects between natal points
            aspect_input_points = {
                name: {'name': data['name'], 'longitude': data['longitude'], 'retrograde': data.get('retrograde', False), 'speed': data.get('speed', 0.0)}
                for name, data in chart_points_with_context.items()
                if 'longitude' in data and data['name'] not in {'Vertex', 'East_Point', 'ImumCoeli', 'Descendant'} # Exclude specific angles from primary aspecting
            }
            chart_aspects = self.aspect_calculator.find_aspects(aspect_input_points)

            # 6. Calculate Fixed Stars (if requested)
            fixed_stars_data = {}
            if include_fixed_stars_positions:
                fixed_stars_data['positions'] = self._calculate_fixed_star_positions(dt_utc, latitude, longitude, elevation, cusps)
            if include_fixed_stars_aspects:
                fixed_stars_data['aspects'] = self._calculate_fixed_star_aspects(chart_points_with_context, dt_utc, latitude, longitude, elevation)
            
            # 7. Calculate Midpoints (if requested)
            midpoints_data = []
            midpoint_hits = []
            if include_midpoints:
                midpoints_data = self.calculate_midpoints(chart_points_with_context)
                midpoint_hits = self._find_midpoint_aspects(chart_points_with_context, midpoints_data, midpoint_orb)

            # 8. Calculate Antiscia & Contra-Antiscia (if requested)
            antiscia_data = {}
            if include_antiscia:
                antiscia_data = self.calculate_antiscia_points(chart_points_with_context)

            # 9. Analyze Chart Signature (Elements, Modalities, Hemispheres)
            chart_signature = self._analyze_chart_signature(chart_points_with_context)


            self._last_calculated_chart_data = {
                'metadata': {
                    'datetime_utc': dt_utc.isoformat(),
                    'latitude': latitude,
                    'longitude': longitude,
                    'elevation': elevation,
                    'house_system': house_system,
                    'zodiac_type': self.zodiac_type,
                    'ayanamsa': self.ayanamsa_name if self.zodiac_type == 'sidereal' else None
                },
                'houses': {
                    'cusps': [round(c, 3) for c in cusps],
                    'angles': {name: round(lon, 3) for name, lon in angles.items()}
                },
                'points': chart_points_with_context, # Contains planets, nodes, and angles with full context
                'aspects': chart_aspects,
                'chart_signature': chart_signature
            }

            if fixed_stars_data:
                self._last_calculated_chart_data['fixed_stars'] = fixed_stars_data
            if arabic_parts_list:
                self._last_calculated_chart_data['arabic_parts'] = arabic_parts_list
            if midpoints_data:
                self._last_calculated_chart_data['midpoints'] = midpoints_data
            if midpoint_hits:
                self._last_calculated_chart_data['midpoint_hits'] = midpoint_hits
            if antiscia_data:
                self._last_calculated_chart_data['antiscia'] = antiscia_data

            self.logger.info("Chart calculation completed successfully and data stored internally.")
            return self._last_calculated_chart_data

        except Exception as e:
            self.logger.error(f"Error calculating chart: {e}", exc_info=True)
            raise RuntimeError(f"Failed to calculate chart: {str(e)}")

    @property
    def julian_day_utc(self) -> Optional[float]:
        """Returns the Julian Day for the currently set chart time."""
        if self._jd_ut is None:
            raise RuntimeError("Julian Day not set. Call calculate_chart() or _set_location_and_time() first.")
        return self._jd_ut

    @property
    def swe_flags(self) -> int:
        """Returns the Swisseph flags used for current calculations."""
        return self._swe_flags

    @property
    def chart_calculated(self) -> bool:
        """Indicates if a chart has been successfully calculated and stored."""
        return self._last_calculated_chart_data is not None

    def get_all_point_details(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves all calculated astrological points (planets, nodes, angles) with their full details.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary mapping point names to their detailed data.
        Raises:
            RuntimeError: If a chart has not been calculated yet.
        """
        if not self.chart_calculated or self._last_calculated_chart_data.get('points') is None:
            raise RuntimeError("Chart has not been calculated or point data is missing. Call calculate_chart() first.")
        return self._last_calculated_chart_data['points']

    def _calculate_all_point_positions_raw(self, points_list: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Calculates raw positions for a list of astrological points (planets, nodes, etc.)
        using Swisseph and the already set Julian Day and topocentric flags.

        Args:
            points_list (List[str]): List of point names (e.g., 'Sun', 'Moon', 'True_Node').

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping point names to their raw calculated data.
                                      Includes 'error' key if calculation for a point fails.
        Raises:
            RuntimeError: If Julian Day is not set.
        """
        if self._jd_ut is None:
            raise RuntimeError("Julian Day not set. Call _set_location_and_time() or ensure calculate_chart() is called.")

        results = {}
        flags = self._swe_flags | swe.FLG_SPEED

        for point_name_str in points_list:
            swe_id = PLANET_ID_MAP.get(point_name_str)
            if swe_id is None:
                self.logger.warning(f"Unknown astrological point: {point_name_str}. Skipping.")
                results[point_name_str] = {"error": "Unknown point name for SWE"}
                continue

            try:
                # Calculate ecliptic coordinates (longitude, latitude, distance, speed)
                pos_ecl, ret_flags_ecl = swe.calc_ut(self._jd_ut, swe_id, flags=flags)
                
                # Calculate equatorial coordinates (RA, Declination)
                pos_eq, ret_flags_eq = swe.calc_ut(self._jd_ut, swe_id, flags=flags | swe.FLG_EQUATORIAL)

                if (ret_flags_ecl & swe.FLG_ERR) or (ret_flags_eq & swe.FLG_ERR):
                    self.logger.warning(f"Error calculating position for {point_name_str} (ID: {swe_id}). Swisseph error flags: {ret_flags_ecl} (ecl), {ret_flags_eq} (eq).")
                    results[point_name_str] = {"error": f"SWE error: ecl={ret_flags_ecl}, eq={ret_flags_eq}"}
                    continue

                speed = pos_ecl[3] # Daily speed in longitude (degrees per day)

                results[point_name_str] = {
                    'name': point_name_str,
                    'longitude': pos_ecl[0] % 360,
                    'ecliptic_latitude': pos_ecl[1],
                    'distance_au': pos_ecl[2],
                    'speed': speed,
                    'retrograde': speed < 0,
                    'right_ascension': pos_eq[0],
                    'declination': pos_eq[1]
                }

            except Exception as e:
                self.logger.error(f"Error calculating position for {point_name_str}: {e}", exc_info=True)
                results[point_name_str] = {"error": f"Exception during calculation: {str(e)}"}
        return results

    def _calculate_essential_dignities(self, planet_name: str, sign_name: str, degree_in_sign: int, is_day_chart: bool) -> Dict[str, Any]:
        """
        Calculates the essential dignities (rulership, exaltation, detriment, fall, triplicity, term, face) for a given planet in a specific sign.
        Based on universally recognized traditional rules hardcoded within ESSENTIAL_DIGNITY_RULES.

        Args:
            planet_name (str): Name of the planet (e.g., "Sun", "Mars").
            sign_name (str): Name of the zodiac sign (e.g., "Aries", "Taurus").
            degree_in_sign (int): Degree of the planet within its sign (0-29).
            is_day_chart (bool): True if it's a day chart (Sun in houses 7-12), False for night chart.

        Returns:
            Dict[str, Any]: Dictionary indicating the dignity status.
        """
        dignities_res = {
            "ruler": False, "exaltation": False, "detriment": False, "fall": False,
            "triplicity_ruler": None, "term_ruler": None, "face_ruler": None,
            "status": "Peregrine" # Default status if no dignities found
        }

        if planet_name not in PLANETS_FOR_ESSENTIAL_DIGNITIES or sign_name not in ZODIAC_SIGNS:
            dignities_res["status"] = "N/A"; return dignities_res # Planet not assessed or sign unknown

        rulerships = ESSENTIAL_DIGNITY_RULES.get("rulerships", {})
        exaltations = ESSENTIAL_DIGNITY_RULES.get("exaltations", {})
        triplicities = ESSENTIAL_DIGNITY_RULES.get("triplicities", {})
        terms = ESSENTIAL_DIGNITY_RULES.get("terms_egyptian", {})
        faces = ESSENTIAL_DIGNITY_RULES.get("faces", {})

        # 1. Rulership & Detriment
        ruler_of_sign = rulerships.get(sign_name)
        if ruler_of_sign == planet_name:
            dignities_res["ruler"] = True
            dignities_res["status"] = "Rulership"
        else:
            try:
                sign_index = ZODIAC_SIGNS.index(sign_name)
                opposite_sign_name = ZODIAC_SIGNS[(sign_index + 6) % 12]
                if rulerships.get(opposite_sign_name) == planet_name:
                    dignities_res["detriment"] = True
                    dignities_res["status"] = "Detriment"
            except ValueError: # Sign not found in ZODIAC_SIGNS
                pass

        # 2. Exaltation & Fall
        exalt_of_sign = exaltations.get(sign_name)
        if exalt_of_sign == planet_name:
            dignities_res["exaltation"] = True
            if dignities_res["status"] == "Peregrine": # Exaltation is a strong dignity
                dignities_res["status"] = "Exaltation"
        else:
            try:
                sign_index = ZODIAC_SIGNS.index(sign_name)
                opposite_sign_name = ZODIAC_SIGNS[(sign_index + 6) % 12]
                if exaltations.get(opposite_sign_name) == planet_name:
                    dignities_res["fall"] = True
                    if dignities_res["status"] == "Peregrine": # Fall is a strong debility
                        dignities_res["status"] = "Fall"
            except ValueError:
                pass

        # 3. Triplicity Ruler
        element = SIGN_TO_ELEMENT.get(sign_name)
        if element and element in triplicities:
            if is_day_chart:
                triplicity_ruler = triplicities[element]["day_ruler"]
            else:
                triplicity_ruler = triplicities[element]["night_ruler"]
            
            dignities_res["triplicity_ruler"] = triplicity_ruler
            if triplicity_ruler == planet_name and dignities_res["status"] == "Peregrine":
                dignities_res["status"] = "Triplicity"

        # 4. Term Ruler
        term_rules_for_sign = terms.get(sign_name)
        if term_rules_for_sign:
            current_degree = degree_in_sign
            for ruler, end_degree in term_rules_for_sign:
                if current_degree < end_degree:
                    dignities_res["term_ruler"] = ruler
                    if ruler == planet_name and dignities_res["status"] == "Peregrine":
                        dignities_res["status"] = "Term"
                    break

        # 5. Face Ruler
        face_rules_for_sign = faces.get(sign_name)
        if face_rules_for_sign:
            face_index = int(degree_in_sign / 10) # 0-9 deg (idx 0), 10-19 deg (idx 1), 20-29 deg (idx 2)
            if face_index < len(face_rules_for_sign):
                face_ruler = face_rules_for_sign[face_index]
                dignities_res["face_ruler"] = face_ruler
                if face_ruler == planet_name and dignities_res["status"] == "Peregrine":
                    dignities_res["status"] = "Face"

        return dignities_res

    def _get_point_longitude_and_lat(self, point_name: str, chart_points: Dict[str, Any], angles: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
        """Helper to get longitude and ecliptic latitude of a point from either chart_points or angles."""
        if point_name in chart_points and 'longitude' in chart_points[point_name]:
            return chart_points[point_name]['longitude'], chart_points[point_name].get('ecliptic_latitude', 0.0)
        elif point_name in angles: # Angles usually have 0 ecliptic latitude
            return angles[point_name], 0.0
        return None, None

    def _calculate_arabic_part_position(self, part_name: str, chart_points: Dict[str, Any], angles: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates the position of a specific Arabic Part.
        Uses formulas hardcoded in ARABIC_PARTS_FORMULAS.

        Args:
            part_name (str): Name of the Arabic Part (e.g., "Part of Fortune").
            chart_points (Dict[str, Any]): Dictionary of all calculated natal points (planets, nodes, angles).
            angles (Dict[str, Any]): Dictionary of natal angles (Ascendant, Midheaven, etc.).

        Returns:
            Dict[str, Any]: Dictionary containing the calculated position and related astrological data.
        """
        formula = ARABIC_PARTS_FORMULAS.get(part_name)
        if not formula:
            error_msg = f"Formula for Arabic Part '{part_name}' not found."
            self.logger.error(error_msg)
            return {"name": part_name, "symbol": POINT_DISPLAY_SYMBOLS.get(part_name, "?"), "error": error_msg}

        asc_lon, _ = self._get_point_longitude_and_lat("Ascendant", chart_points, angles)
        plus_body_lon, _ = self._get_point_longitude_and_lat(formula['plus'], chart_points, angles)
        minus_body_lon, _ = self._get_point_longitude_and_lat(formula['minus'], chart_points, angles)

        if asc_lon is None or plus_body_lon is None or minus_body_lon is None:
            error_msg = f"Essential point data missing for {part_name} ({formula['plus']}, {formula['minus']}, or Ascendant)."
            self.logger.error(error_msg)
            return {"name": part_name, "symbol": POINT_DISPLAY_SYMBOLS.get(part_name, "?"), "error": error_msg}

        # Special handling for Part of Fortune day/night formula
        pof_longitude = 0.0
        if part_name == "Part of Fortune":
            sun_data = chart_points.get("Sun")
            sun_house = sun_data.get("house") if sun_data else None
            is_day_chart = False
            if sun_house is not None:
                # Sun in houses 7-12 is above horizon (day chart)
                is_day_chart = (7 <= sun_house <= 12)
            else:
                self.logger.warning("Sun's house not determined for Part of Fortune day/night calculation. Defaulting to day formula.")
                is_day_chart = True

            if is_day_chart: # Day Chart: Ascendant + Moon - Sun
                pof_longitude = (asc_lon + chart_points['Moon']['longitude'] - chart_points['Sun']['longitude']) % 360.0
            else: # Night Chart: Ascendant + Sun - Moon
                pof_longitude = (asc_lon + chart_points['Sun']['longitude'] - chart_points['Moon']['longitude']) % 360.0
        elif part_name == "Part of Marriage (Day)": # Specific formula if day chart
             sun_data = chart_points.get("Sun")
             sun_house = sun_data.get("house") if sun_data else None
             is_day_chart = False
             if sun_house is not None: is_day_chart = (7 <= sun_house <= 12)
             if is_day_chart:
                 pof_longitude = (asc_lon + plus_body_lon - minus_body_lon) % 360.0
             else:
                 return {"name": part_name, "symbol": POINT_DISPLAY_SYMBOLS.get(part_name, "?"), "error": f"Part of Marriage (Day) not applicable for night chart."}
        elif part_name == "Part of Marriage (Night)": # Specific formula if night chart
            sun_data = chart_points.get("Sun")
            sun_house = sun_data.get("house") if sun_data else None
            is_day_chart = False
            if sun_house is not None: is_day_chart = (7 <= sun_house <= 12)
            if not is_day_chart:
                pof_longitude = (asc_lon + plus_body_lon - minus_body_lon) % 360.0
            else:
                return {"name": part_name, "symbol": POINT_DISPLAY_SYMBOLS.get(part_name, "?"), "error": f"Part of Marriage (Night) not applicable for day chart."}
        else: # Standard formula: Ascendant + Body1 - Body2
            pof_longitude = (asc_lon + plus_body_lon - minus_body_lon) % 360.0

        # Format Arabic Part data
        part_details = self._format_point_data(part_name, pof_longitude, speed_deg_per_day=0.0, ecliptic_latitude_deg=0.0) # Arabic parts are on the ecliptic
        
        # Calculate RA and Declination for the Arabic Part (which is on the ecliptic for latitude=0)
        try:
            (ra_part, dec_part, _) = swe.ecl_to_eq(self._jd_ut, pof_longitude, 0.0)
            part_details['right_ascension'] = round(ra_part, 3)
            part_details['declination'] = round(dec_part, 3)
        except Exception as e:
            self.logger.warning(f"Could not calculate RA/Dec for {part_name}: {e}. Setting to 0.0.")

        # Determine house for the Arabic Part
        house_cusps_list = self._last_calculated_chart_data['houses']['cusps'] if self._last_calculated_chart_data else None
        if house_cusps_list:
            part_details["house"] = self.house_calculator.get_house_positions({part_name: pof_longitude}, house_cusps_list).get(part_name)
        else:
            part_details["house"] = None
            self.logger.warning(f"House cusps data unavailable for {part_name} house placement.")
            
        return part_details

    def _calculate_fixed_star_positions(self, dt_utc: datetime, latitude: float, longitude: float, elevation: float, house_cusps: List[float]) -> List[Dict[str, Any]]:
        """
        Calculates positions of a hardcoded set of major fixed stars for a given date, time, and location using Swisseph.

        Args:
            dt_utc (datetime): UTC datetime for the calculation.
            latitude (float): Observer's latitude in degrees.
            longitude (float): Observer's longitude in degrees.
            elevation (float): Observer's elevation in meters.
            house_cusps (List[float]): The 12 house cusp longitudes of the chart for house placement.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a fixed star
                                  with its calculated astrological and astronomical data.
        """
        fixed_stars_results = []
        jd_ut_calc = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
        )
        swe_flags_calc = swe.FLG_SWIEPH | swe.FLG_TOPOCTR # Use topocentric flags

        # Ensure observer location is set for fixed stars calculation
        swe.set_topo(longitude, latitude, elevation)
        self.logger.debug(f"Swisseph topocentric set for fixed stars to Lat: {latitude}, Lon: {longitude}, Elev: {elevation}")

        for star_name_key, star_info in FIXED_STAR_J2000_DATA.items():
            swe_star_name = star_info.get("swe_name", f",{star_name_key}")

            try:
                # swe.fixstar_ut automatically handles precession to the date for fixed stars.
                ret_ecl, err_ecl = swe.fixstar_ut(swe_star_name, jd_ut_calc, swe_flags_calc)
                ret_eq, err_eq = swe.fixstar_ut(swe_star_name, jd_ut_calc, swe_flags_calc | swe.FLG_EQUATORIAL)

                if (err_ecl and err_ecl.strip().startswith('-')) or \
                   (err_eq and err_eq.strip().startswith('-')):
                    self.logger.warning(f"Could not calculate position for fixed star '{swe_star_name}'. "
                                       f"Ecliptic Error: {err_ecl}, Equatorial Error: {err_eq}. Skipping.")
                    continue

                lon_ecl = ret_ecl[0] % 360 # Longitude
                lat_ecl = ret_ecl[1]   # Ecliptic latitude
                ra_eq = ret_eq[0]      # Right Ascension
                dec_eq = ret_eq[1]     # Declination

                sign_info = self.house_calculator.get_sign_and_degree(lon_ecl)
                
                star_result = {
                    'name': star_name_key,
                    'key': star_name_key.lower().replace(" ", "_"),
                    'symbol': POINT_DISPLAY_SYMBOLS.get("Fixed Star", "★"),
                    'bayer_designation': star_info.get('bayer_designation', 'N/A'),
                    'constellation': star_info.get('constellation', 'N/A'),
                    'magnitude': star_info.get('magnitude', 'N/A'),
                    'longitude': round(lon_ecl, 3),
                    'ecliptic_latitude': round(lat_ecl, 3),
                    'right_ascension': round(ra_eq, 3),
                    'declination': round(dec_eq, 3),
                    'sign_name': sign_info['sign_name'],
                    'degree_in_sign': sign_info['degree_in_sign'],
                    'minute_in_sign': sign_info['minute_in_sign'],
                    'second_in_sign': sign_info['second_in_sign'],
                    'speed': 0.0, 'retrograde': False, 'distance_au': 0.0, # Not applicable for fixed stars
                    'dignities': {"status": "N/A"}, # Not applicable
                }
                
                # Determine house for the fixed star
                if house_cusps:
                    star_result["house"] = self.house_calculator.get_house_positions({star_name_key: lon_ecl}, house_cusps).get(star_name_key)
                else:
                    star_result["house"] = None

                fixed_stars_results.append(star_result)

            except Exception as e:
                self.logger.error(f"Error calculating position for fixed star {star_name_key}: {str(e)}", exc_info=True)
        return fixed_stars_results

    def _calculate_fixed_star_aspects(self, chart_points: Dict[str, Any], dt_utc: datetime, latitude: float, longitude: float, elevation: float,
                                      orb_longitude: float = 1.0, orb_declination_parallel: float = 0.5) -> List[Dict[str, Any]]:
        """
        Calculates specific aspects (conjunctions, oppositions in longitude, and parallels/contra-parallels
        in declination) between major fixed stars and chart points.

        Args:
            chart_points (Dict[str, Any]): All calculated chart points (planets, angles).
            dt_utc (datetime): UTC datetime of the chart.
            latitude (float): Observer's geographic latitude in degrees.
            longitude (float): Observer's longitude in degrees.
            elevation (float): Observer's elevation in meters.
            orb_longitude (float): Orb (in degrees) for longitudinal conjunction and opposition.
            orb_declination_parallel (float): Orb (in degrees) for declination parallels and contra-parallels.

        Returns:
            List[Dict[str, Any]]: A sorted list of dictionaries, each describing a significant
                                  fixed star aspect with a chart point.
        """
        fixed_star_aspects = []
        jd_ut_calc = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
        swe_flags_calc = swe.FLG_SWIEPH | swe.FLG_TOPOCTR

        # Set observer location for topocentric calculations for fixed stars
        swe.set_topo(longitude, latitude, elevation)

        for star_key, star_info in FIXED_STAR_J2000_DATA.items():
            swe_star_name = star_info.get("swe_name", f",{star_key}")

            try:
                star_pos_ecl, err_ecl = swe.fixstar_ut(swe_star_name, jd_ut_calc, swe_flags_calc)
                star_pos_eq, err_eq = swe.fixstar_ut(swe_star_name, jd_ut_calc, swe_flags_calc | swe.FLG_EQUATORIAL)

                if (err_ecl and err_ecl.strip().startswith('-')) or \
                   (err_eq and err_eq.strip().startswith('-')):
                    self.logger.warning(f"Could not calculate position for fixed star {swe_star_name} for aspects. Skipping.")
                    continue

                star_longitude_ecl = star_pos_ecl[0]
                star_declination_eq = star_pos_eq[1]

                for point_name, point_data in chart_points.items():
                    # Only consider points that have a valid longitude and are not error states
                    if 'longitude' not in point_data or 'error' in point_data:
                        continue
                    
                    point_longitude_ecl = point_data["longitude"]
                    point_declination_eq = point_data.get("declination") # From calculated point data

                    # 1. Longitudinal Conjunction / Opposition
                    diff_lon = abs(point_longitude_ecl - star_longitude_ecl)
                    if diff_lon > 180: diff_lon = 360 - diff_lon

                    # Conjunction
                    if diff_lon <= orb_longitude:
                        fixed_star_aspects.append({
                            "star_name": star_key,
                            "planet_name": point_name,
                            "aspect_type": "Conjunction (Longitude)",
                            "orb_degrees": round(diff_lon, 3),
                            "star_longitude": round(star_longitude_ecl, 3),
                            "planet_longitude": round(point_longitude_ecl, 3)
                        })
                    
                    # Opposition
                    orb_for_opposition_check = abs(diff_lon - 180.0)
                    if orb_for_opposition_check <= orb_longitude:
                        fixed_star_aspects.append({
                            "star_name": star_key,
                            "planet_name": point_name,
                            "aspect_type": "Opposition (Longitude)",
                            "orb_degrees": round(orb_for_opposition_check, 3),
                            "star_longitude": round(star_longitude_ecl, 3),
                            "planet_longitude": round(point_longitude_ecl, 3)
                        })

                    # 2. Parallel / Contra-Parallel in Declination
                    if point_declination_eq is not None:
                        # Parallel (same declination, same side of equator)
                        diff_dec = abs(point_declination_eq - star_declination_eq)
                        if diff_dec <= orb_declination_parallel:
                            fixed_star_aspects.append({
                                "star_name": star_key,
                                "planet_name": point_name,
                                "aspect_type": "Parallel (Declination)",
                                "orb_degrees": round(diff_dec, 3),
                                "star_declination": round(star_declination_eq, 3),
                                "planet_declination": round(point_declination_eq, 3)
                            })

                        # Contra-Parallel (same declination, opposite sides of equator)
                        # Check that they are on opposite sides of the equator, but within orb
                        if (point_declination_eq * star_declination_eq < 0) and abs(point_declination_eq + star_declination_eq) <= orb_declination_parallel:
                            fixed_star_aspects.append({
                                "star_name": star_key,
                                "planet_name": point_name,
                                "aspect_type": "Contra-Parallel (Declination)",
                                "orb_degrees": round(abs(point_declination_eq + star_declination_eq), 3),
                                "star_declination": round(star_declination_eq, 3),
                                "planet_declination": round(point_declination_eq, 3)
                            })
            except Exception as e:
                self.logger.error(f"Error calculating aspects for fixed star {star_key}: {e}", exc_info=True)
        
        self.logger.info(f"Calculated {len(fixed_star_aspects)} fixed star aspects.")
        return sorted(fixed_star_aspects, key=lambda x: x['orb_degrees'])

    def calculate_midpoints(self, chart_points: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculates all 90-degree zodiacal midpoints for all pairs of chart points.

        Args:
            chart_points (Dict[str, Any]): Dictionary of all calculated natal points (planets, angles, etc.).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a midpoint.
        """
        midpoints = []
        points_list = [p for p in chart_points.values() if 'longitude' in p and 'error' not in p]
        
        for i in range(len(points_list)):
            for j in range(i + 1, len(points_list)):
                p1 = points_list[i]
                p2 = points_list[j]

                lon1 = p1['longitude']
                lon2 = p2['longitude']

                # Calculate the midpoint (shortest arc)
                midpoint_lon_raw = (lon1 + lon2) / 2.0
                # If the shortest arc crosses 0/360 boundary, need to adjust midpoint
                diff = abs(lon1 - lon2)
                if diff > 180: # The arc crosses 0 Aries/Libra
                    midpoint_lon = (midpoint_lon_raw + 180) % 360 # Add 180 to shift to the other side
                else:
                    midpoint_lon = midpoint_lon_raw

                midpoint_lon %= 360

                midpoint_name = f"{p1['name']}/{p2['name']}"
                midpoint_details = self._format_point_data(midpoint_name, midpoint_lon)
                midpoint_details['type'] = 'Midpoint'
                midpoint_details['point1_name'] = p1['name']
                midpoint_details['point2_name'] = p2['name']
                midpoint_details['dignities'] = {"status": "N/A"} # Dignities not applicable
                midpoint_details['house'] = None # Requires separate house calculation if needed (not standard)

                midpoints.append(midpoint_details)
                
        self.logger.info(f"Calculated {len(midpoints)} midpoints.")
        return midpoints

    def _find_midpoint_aspects(self, chart_points: Dict[str, Any], midpoints: List[Dict[str, Any]], orb: float = 1.0) -> List[Dict[str, Any]]:
        """
        Finds aspects between chart points and calculated midpoints.

        Args:
            chart_points (Dict[str, Any]): Dictionary of all calculated natal points.
            midpoints (List[Dict[str, Any]]): List of calculated midpoints.
            orb (float): The maximum orb for a midpoint "hit".

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a midpoint hit.
        """
        midpoint_hits = []
        
        # Points to check against midpoints (usually planets/angles)
        aspecting_points = {
            name: {'name': data['name'], 'longitude': data['longitude']}
            for name, data in chart_points.items()
            if 'longitude' in data and data['name'] not in {'Vertex', 'East_Point'} # Exclude less commonly aspected points
        }
        
        for mp in midpoints:
            mp_lon = mp['longitude']
            
            for pt_name, pt_data in aspecting_points.items():
                pt_lon = pt_data['longitude']
                
                diff_abs = abs(mp_lon - pt_lon)
                normalized_diff = diff_abs
                if normalized_diff > 180:
                    normalized_diff = 360 - normalized_diff
                
                # Check for Conjunction (0 deg) and Opposition (180 deg) hits only
                # These are the most common and powerful midpoint hits
                
                # Conjunction hit
                if abs(normalized_diff - 0) <= orb:
                    midpoint_hits.append({
                        "midpoint": mp['name'],
                        "point": pt_name,
                        "aspect_type": "Conjunction (Midpoint Hit)",
                        "angle": 0,
                        "actual_angle": round(normalized_diff, 3),
                        "orb": round(abs(normalized_diff - 0), 3)
                    })
                
                # Opposition hit
                if abs(normalized_diff - 180) <= orb:
                    midpoint_hits.append({
                        "midpoint": mp['name'],
                        "point": pt_name,
                        "aspect_type": "Opposition (Midpoint Hit)",
                        "angle": 180,
                        "actual_angle": round(normalized_diff, 3),
                        "orb": round(abs(normalized_diff - 180), 3)
                    })
        
        self.logger.info(f"Calculated {len(midpoint_hits)} midpoint hits.")
        return sorted(midpoint_hits, key=lambda x: x['orb'])

    def calculate_antiscia_points(self, chart_points: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Calculates Antiscia (points equidistant from 0 Cancer/Capricorn - the solstitial axis) and Contra-Antiscia (points equidistant from 0 Aries/Libra - the equinoctial axis).
        These are also known as parallels of obliquity or aversion.

        Args:
            chart_points (Dict[str, Any]): All calculated chart points (planets, angles).

        Returns:
            Dict[str, List[Dict[str, Any]]]: Contains lists of 'antiscia' and 'contra_antiscia' points.
        """
        antiscia_points = []
        contra_antiscia_points = []

        if self._jd_ut is None:
            raise RuntimeError("Julian Day not set. Call _set_location_and_time() or ensure calculate_chart() is called.")

        for point_name, point_data in chart_points.items():
            if 'longitude' not in point_data or 'error' in point_data:
                continue
            
            # Skip Antiscia/Contra-Antiscia calculation for the angles themselves, or derived points
            if point_name in ['Ascendant', 'Midheaven', 'ImumCoeli', 'Descendant', 'Vertex', 'East_Point'] or \
               'Part of' in point_name or 'Antiscia' in point_name or 'Midpoint' in point_name:
                continue

            lon = point_data['longitude']
            ecl_lat = point_data.get('ecliptic_latitude', 0.0) # Use the actual ecliptic latitude of the point

            # Antiscia: Symmetrical to 0 Cancer (90°) and 0 Capricorn (270°)
            # Axis of symmetry: Solstice points (90 and 270 degrees)
            antiscia_lon = (180 - lon) % 360 # This formula correctly mirrors around the 90/270 axis.
            
            # Contra-Antiscia: Symmetrical to 0 Aries (0°) and 0 Libra (180°)
            # Axis of symmetry: Equinox points (0 and 180 degrees)
            contra_antiscia_lon = (360 - lon) % 360 # This formula correctly mirrors around the 0/180 axis.

            # For Antiscia, the ecliptic latitude should be the same as the original point.
            # For Contra-Antiscia, the ecliptic latitude should be the opposite of the original point.
            
            # Calculate RA/Dec for Antiscia
            ra_ant, dec_ant = 0.0, 0.0
            try:
                # Use swe.ecl_to_eq to get RA/Dec from the new longitude and original ecliptic latitude
                (ra_ant, dec_ant, _) = swe.ecl_to_eq(self._jd_ut, antiscia_lon, ecl_lat)
            except Exception as e:
                self.logger.warning(f"Could not calculate RA/Dec for Antiscia {point_name}: {e}")

            antiscia_details = self._format_point_data(
                f"Antiscia {point_name}", antiscia_lon,
                ecliptic_latitude_deg=ecl_lat, # Antiscia has same ecliptic latitude as source
                right_ascension_deg=ra_ant, declination_deg=dec_ant,
                speed_deg_per_day=0.0 # Derived point has no intrinsic speed
            )
            antiscia_details['source_point'] = point_name
            antiscia_details['type'] = 'Antiscia'
            antiscia_details['dignities'] = {"status": "N/A"}
            antiscia_details['house'] = self.house_calculator.get_house_positions({antiscia_details['name']: antiscia_lon}, self._last_calculated_chart_data['houses']['cusps']).get(antiscia_details['name']) if self._last_calculated_chart_data else None
            antiscia_points.append(antiscia_details)

            # Calculate RA/Dec for Contra-Antiscia
            ra_cont_ant, dec_cont_ant = 0.0, 0.0
            try:
                # Use swe.ecl_to_eq to get RA/Dec from the new longitude and *opposite* ecliptic latitude
                (ra_cont_ant, dec_cont_ant, _) = swe.ecl_to_eq(self._jd_ut, contra_antiscia_lon, -ecl_lat)
            except Exception as e:
                self.logger.warning(f"Could not calculate RA/Dec for Contra-Antiscia {point_name}: {e}")

            contra_antiscia_details = self._format_point_data(
                f"Contra-Antiscia {point_name}", contra_antiscia_lon,
                ecliptic_latitude_deg=-ecl_lat, # Contra-Antiscia has opposite ecliptic latitude as source
                right_ascension_deg=ra_cont_ant, declination_deg=dec_cont_ant,
                speed_deg_per_day=0.0 # Derived point has no intrinsic speed
            )
            contra_antiscia_details['source_point'] = point_name
            contra_antiscia_details['type'] = 'Contra-Antiscia'
            contra_antiscia_details['dignities'] = {"status": "N/A"}
            contra_antiscia_details['house'] = self.house_calculator.get_house_positions({contra_antiscia_details['name']: contra_antiscia_lon}, self._last_calculated_chart_data['houses']['cusps']).get(contra_antiscia_details['name']) if self._last_calculated_chart_data else None
            contra_antiscia_points.append(contra_antiscia_details)
        
        self.logger.info(f"Calculated {len(antiscia_points)} Antiscia and {len(contra_antiscia_points)} Contra-Antiscia points.")
        return {'antiscia': antiscia_points, 'contra_antiscia': contra_antiscia_points}

    def _analyze_chart_signature(self, chart_points: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the distribution of planets across elements, modalities, and hemispheres.

        Args:
            chart_points (Dict[str, Any]): All calculated chart points (planets, angles, etc.).

        Returns:
            Dict[str, Any]: A summary of the chart's signature.
        """
        signature = {
            "elements": {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0},
            "modalities": {"Cardinal": 0, "Fixed": 0, "Mutable": 0},
            "hemispheres": {"North": 0, "South": 0, "East": 0, "West": 0},
            "total_points": 0
        }

        # Consider only planetary bodies for signature, excluding angles and derived points
        points_for_signature = [
            p for p in chart_points.values()
            if p['name'] in PLANET_ID_MAP and 'longitude' in p and 'error' not in p
        ]
        
        signature["total_points"] = len(points_for_signature)

        for point_data in points_for_signature:
            sign_name = point_data['sign_name']
            
            # Elements
            element = SIGN_TO_ELEMENT.get(sign_name)
            if element:
                signature["elements"][element] += 1
            
            # Modalities
            modality = SIGN_TO_MODALITY.get(sign_name)
            if modality:
                signature["modalities"][modality] += 1

            # Hemispheres (rough calculation based on longitude relative to Asc/Desc for East/West and MC/IC for North/South)
            # This is a simplification; precise hemisphere analysis relies on house placements relative to horizon/meridian
            # For general chart signature, we use the basic ecliptic approach.
            longitude = point_data['longitude']
            
            # North/South: Northern hemisphere of the ecliptic (0-180 Aries to Libra) or Southern (180-360 Libra to Aries)
            # This is not about celestial equator, but ecliptic halves.
            # However, astrological hemisphere is usually North/South of the *celestial equator* (based on declination)
            # and East/West of the *meridian* (based on longitude relative to Asc/Desc, but not necessarily ecliptic halves).
            # For simplicity for this overview, I'll use a very basic longitude-based approach for hemispheres.
            # A more robust approach would use actual declination (for North/South) and house placement for East/West.
            
            # Let's use declination for North/South for accuracy
            declination = point_data.get('declination', 0.0)
            if declination >= 0:
                signature["hemispheres"]["North"] += 1
            else:
                signature["hemispheres"]["South"] += 1
            
            # East/West: East is usually 1st to 6th houses, West is 7th to 12th houses (related to Ascendant)
            # For a general signature without specific house data, consider direct vs. inverse aspects to ASC/DESC axis:
            # East (Self-determined): 10th-3rd house segment (from MC to IC via Asc)
            # West (Other-determined): 4th-9th house segment (from IC to MC via Desc)
            # A simpler way without house cusps is to check longitude relative to the Ascendant, but this depends on chart orientation.
            # For simplicity for 'signature', I'll use traditional chart quadrant.
            
            # A common, simplified astrological hemisphere definition for signature is based on the MC-IC axis.
            # Above the horizon (MC-IC via Asc): North (day)
            # Below the horizon (IC-MC via Desc): South (night)
            # This is not consistent with standard 'North/South' hemispheres based on declination.

            # Re-evaluate the Hemisphere logic for "signature" to align with common astrological understanding.
            # North/South: Planets with North declination vs. South declination.
            # East/West: Planets in the Eastern hemisphere (Asc to MC to IC) vs. Western (Desc to IC to MC).
            # This would require angles (Asc/Desc/MC/IC) to properly define the quadrants.
            # Since chart_points includes angles, we can use them.
            
            asc_lon = chart_points.get('Ascendant', {}).get('longitude')
            desc_lon = chart_points.get('Descendant', {}).get('longitude')
            mc_lon = chart_points.get('Midheaven', {}).get('longitude')
            ic_lon = chart_points.get('ImumCoeli', {}).get('longitude')

            if asc_lon is not None and mc_lon is not None:
                # East: Asc -> MC -> IC (via Asc) to Desc
                # West: Desc -> IC -> MC (via Desc) to Asc
                # This depends on which direction the zodiac is read.
                # A common simpler definition: East of Meridian (MC/IC axis), West of Meridian.
                # Or based on Ascendant: Eastern hemisphere is from Ascendant counter-clockwise to Descendant.
                
                # Let's use the Ascendant as the dividing line for East/West.
                # East = Ascendant (0deg relative to Asc) to Descendant (180deg relative to Asc)
                # This is problematic for wrap-around.

                # Best approach for East/West: Determine if point is in the "Eastern" or "Western" half based on the chart.
                # Eastern Hemisphere: from 1st house cusp (Asc) counter-clockwise to 12th, 11th, 10th, 9th, 8th.
                # Or, more simply, if the point is in a house from 1 to 6 (Eastern) or 7 to 12 (Western).
                # This requires house calculation to be complete on the point data.
                point_house = point_data.get('house')
                if point_house:
                    if 1 <= point_house <= 6:
                        signature["hemispheres"]["East"] += 1
                    elif 7 <= point_house <= 12:
                        signature["hemispheres"]["West"] += 1
                
                # North/South based on Meridian (MC/IC axis)
                # North: 7th to 12th houses (planets above the horizon)
                # South: 1st to 6th houses (planets below the horizon)
                # This is traditional. Note that this is NOT the celestial equator.
                if point_house:
                    if 7 <= point_house <= 12: # Above horizon
                        signature["hemispheres"]["North"] += 1
                    elif 1 <= point_house <= 6: # Below horizon
                        signature["hemispheres"]["South"] += 1


        return signature


    def calculate_transits(
        self,
        natal_chart_data: Dict[str, Any],
        transit_dt_utc: datetime,
        transit_latitude: float,
        transit_longitude: float,
        elevation: float = 0.0,
        transiting_points_to_include: Optional[List[str]] = None,
        natal_points_to_aspect: Optional[List[str]] = None,
        include_fixed_stars_transit_aspects: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates transiting planetary positions and their aspects to natal chart points.
        Optionally includes fixed stars transiting aspects to natal chart.

        Args:
            natal_chart_data (Dict[str, Any]): The full natal chart data (output of calculate_chart).
            transit_dt_utc (datetime): UTC datetime for the transits.
            transit_latitude (float): Observer's latitude for transits.
            transit_longitude (float): Observer's longitude for transits.
            elevation (float): Observer's elevation for transits.
            transiting_points_to_include (List[str], optional): List of transiting planet names to calculate.
                                                                 Defaults to all in PLANET_ID_MAP.
            natal_points_to_aspect (List[str], optional): List of natal points to check aspects against.
                                                           Defaults to all natal planets and angles.
            include_fixed_stars_transit_aspects (bool): If True, calculates and includes fixed star aspects to natal points.

        Returns:
            Dict[str, Any]: Contains transit positions, transit-to-natal aspects, and optional fixed star transit data.
        Raises:
            ValueError: If natal_chart_data is malformed.
            RuntimeError: If underlying swisseph calculations fail.
        """
        self.logger.info(f"Calculating transits for {transit_dt_utc} to natal chart from {natal_chart_data['metadata']['datetime_utc']}")

        if 'points' not in natal_chart_data or not isinstance(natal_chart_data['points'], dict):
            raise ValueError("Natal chart data is missing 'points' key or it's not a dictionary.")

        natal_points = natal_chart_data['points']

        # Set location and time for transit calculations. This applies to transiting points.
        self._set_location_and_time(transit_dt_utc, transit_latitude, transit_longitude, elevation)

        # Determine which transiting points to include
        if transiting_points_to_include is None:
            transiting_points_to_include = list(PLANET_ID_MAP.keys())

        # Calculate positions of transiting points
        transiting_positions_raw = self._calculate_all_point_positions_raw(transiting_points_to_include)

        transiting_points_with_context = {}
        transiting_points_for_aspect_calc = {}
        for name, raw_data in transiting_positions_raw.items():
            if "error" in raw_data:
                transiting_points_with_context[name] = {"name": name, "error": raw_data['error'], "symbol": POINT_DISPLAY_SYMBOLS.get(name, "?")}
                continue

            point_detail = self._format_point_data(
                name, raw_data['longitude'], raw_data['speed'], raw_data['ecliptic_latitude'],
                raw_data['right_ascension'], raw_data['declination']
            )
            transiting_points_with_context[name] = point_detail
            transiting_points_for_aspect_calc[name] = { # Prepared for aspect calculation
                'name': name, 'longitude': raw_data['longitude'], 'speed': raw_data['speed'], 'retrograde': raw_data['retrograde']
            }

        # Prepare natal points for aspect calculation
        if natal_points_to_aspect is None:
            # Default to all major natal points (planets, nodes, Ascendant, Midheaven, IC, Descendant) for aspecting
            natal_points_to_aspect = [
                p for p in natal_points.keys() 
                if p in PLANET_ID_MAP or p in ['Ascendant', 'Midheaven', 'ImumCoeli', 'Descendant']
            ]

        natal_points_for_aspecting_input = {
            name: {'name': natal_points[name]['name'], 'longitude': natal_points[name]['longitude'],
                   'speed': natal_points[name].get('speed', 0.0), 'retrograde': natal_points[name].get('retrograde', False)}
            for name in natal_points_to_aspect if name in natal_points and 'longitude' in natal_points[name]
        }
        
        # Calculate aspects between transiting points and natal points
        transit_aspects = []
        # Create a combined list for AspectCalculator
        combined_points_for_aspects = {
            f"transit_{k}": v for k, v in transiting_points_for_aspect_calc.items()
        }
        combined_points_for_aspects.update({
            f"natal_{k}": v for k, v in natal_points_for_aspecting_input.items()
        })

        for transiting_name, transiting_data in transiting_points_for_aspect_calc.items():
            for natal_name, natal_data in natal_points_for_aspecting_input.items():
                diff_abs = abs(transiting_data['longitude'] - natal_data['longitude'])
                normalized_diff = diff_abs
                if normalized_diff > 180:
                    normalized_diff = 360 - normalized_diff

                for aspect_def in self.aspect_calculator.aspect_definitions:
                    aspect_name = aspect_def['name']
                    aspect_angle = aspect_def['angle']
                    base_orb = aspect_def['orb'].get('default', 1.0)

                    if (transiting_name in LUMINARIES or natal_name in LUMINARIES) and 'luminaries' in aspect_def['orb']:
                        base_orb = aspect_def['orb']['luminaries']

                    if abs(normalized_diff - aspect_angle) <= base_orb:
                        # Determine if applying or separating.
                        transiting_lon_future = (transiting_data['longitude'] + transiting_data['speed']) % 360
                        
                        # Only consider the transiting point's speed for applying/separating for transit aspects
                        # Natal points are considered fixed for this determination.
                        diff_future = abs(transiting_lon_future - natal_data['longitude'])
                        if diff_future > 180:
                            diff_future = 360 - diff_future
                            
                        current_deviation = abs(normalized_diff - aspect_angle)
                        future_deviation = abs(diff_future - aspect_angle)
                        
                        is_applying = False
                        if future_deviation < current_deviation:
                            is_applying = True

                        transit_aspects.append({
                            'transiting_point': transiting_name,
                            'natal_point': natal_name,
                            'aspect_type': aspect_name,
                            'angle': aspect_angle,
                            'actual_angle': round(normalized_diff, 3),
                            'orb': round(abs(normalized_diff - aspect_angle), 3),
                            'applying': is_applying,
                            'transiting_longitude': round(transiting_data['longitude'], 3),
                            'natal_longitude': round(natal_data['longitude'], 3)
                        })
        self.logger.info(f"Found {len(transit_aspects)} transit aspects.")

        # Integrate Fixed Stars Transits (if requested)
        fixed_stars_transit_data = {}
        if include_fixed_stars_transit_aspects:
            # Fixed stars aspects to natal points at the transit moment
            # Pass the natal points for fixed star aspect calculation
            # Use transit location and time for fixed star positions.
            fixed_stars_transit_data['aspects_to_natal'] = self._calculate_fixed_star_aspects(
                natal_points, 
                transit_dt_utc,
                transit_latitude,
                transit_longitude,
                elevation,
                orb_longitude=1.0, 
                orb_declination_parallel=0.5
            )

        transit_chart_result = {
            'transit_datetime_utc': transit_dt_utc.isoformat(),
            'transiting_positions': transiting_points_with_context,
            'transit_aspects_to_natal': sorted(transit_aspects, key=lambda x: x['orb'])
        }

        if fixed_stars_transit_data:
            transit_chart_result['fixed_stars_transits'] = fixed_stars_transit_data

        return transit_chart_result

    def calculate_progressions(
        self,
        natal_chart_data: Dict[str, Any],
        progression_dt_utc: datetime,
        progression_type: str = 'secondary', # 'secondary' or 'solar_arc'
        points_to_progress: Optional[List[str]] = None,
        include_fixed_stars_progression_aspects: bool = False # New for progressions
    ) -> Dict[str, Any]:
        """
        Calculates progressed planetary positions and their aspects to natal chart points.
        Supports Secondary Progressions and Solar Arc Directions.

        Args:
            natal_chart_data (Dict[str, Any]): The full natal chart data.
            progression_dt_utc (datetime): UTC datetime for the progression (e.g., today's date for a daily horoscope).
            progression_type (str): Type of progression: 'secondary' or 'solar_arc'.
            points_to_progress (List[str], optional): List of point names to progress. Defaults to natal planets/angles.
            include_fixed_stars_progression_aspects (bool): If True, calculates and includes fixed star aspects to progressed points.

        Returns:
            Dict[str, Any]: Contains progressed positions and progressed-to-natal aspects.
        Raises:
            ValueError: If natal_chart_data is malformed or an unsupported progression_type is given.
            RuntimeError: If underlying swisseph calculations fail.
        """
        self.logger.info(f"Calculating {progression_type} progressions for {progression_dt_utc} to natal chart from {natal_chart_data['metadata']['datetime_utc']}")

        if 'metadata' not in natal_chart_data or 'points' not in natal_chart_data:
            raise ValueError("Natal chart data is malformed (missing 'metadata' or 'points').")

        natal_dt_utc = datetime.fromisoformat(natal_chart_data['metadata']['datetime_utc'])
        natal_points = natal_chart_data['points']
        natal_lat = natal_chart_data['metadata']['latitude']
        natal_lon = natal_chart_data['metadata']['longitude']
        natal_elevation = natal_chart_data['metadata'].get('elevation', 0.0)
        natal_house_system = natal_chart_data['metadata'].get('house_system', 'P')

        if points_to_progress is None:
            # Default to all natal planets and angles for progression
            points_to_progress = [p for p in natal_points.keys() if p in PLANET_ID_MAP or p in ['Ascendant', 'Midheaven', 'ImumCoeli', 'Descendant']]

        progressed_positions_with_context = {}
        
        if progression_type == 'secondary':
            # Secondary Progressions: 1 day in ephemeris = 1 year in life.
            # Calculate age in years (including fractions).
            years_passed = (progression_dt_utc - natal_dt_utc).total_seconds() / (365.25 * 24 * 3600) # Use tropical year approximation

            # The ephemeris date used for calculation is natal date + years_passed_in_days.
            ephemeris_date_for_progression = natal_dt_utc + timedelta(days=years_passed)
            
            self.logger.debug(f"Natal date: {natal_dt_utc}, Prog date: {progression_dt_utc}, Years passed: {years_passed:.2f}")
            self.logger.debug(f"Ephemeris date for secondary progression: {ephemeris_date_for_progression}")

            # Set swisseph for the progressed ephemeris date, at natal location for progressed calculations.
            self._set_location_and_time(ephemeris_date_for_progression, natal_lat, natal_lon, natal_elevation)

            for point_name in points_to_progress:
                swe_id = PLANET_ID_MAP.get(point_name)
                if swe_id is not None: # It's a planet/node (Swisseph body)
                    try:
                        pos_ecl, ret_flags_ecl = swe.calc_ut(self._jd_ut, swe_id, flags=self._swe_flags | swe.FLG_SPEED)
                        pos_eq, ret_flags_eq = swe.calc_ut(self._jd_ut, swe_id, flags=self._swe_flags | swe.FLG_EQUATORIAL)

                        if (ret_flags_ecl & swe.FLG_ERR) or (ret_flags_eq & swe.FLG_ERR):
                            self.logger.warning(f"Error progressing {point_name} for secondary progressions. Swisseph error flags: {ret_flags_ecl} (ecl), {ret_flags_eq} (eq). Skipping.")
                            continue

                        prog_lon = pos_ecl[0] % 360
                        prog_lat = pos_ecl[1]
                        prog_speed = pos_ecl[3]
                        prog_distance = pos_ecl[2]
                        prog_retrograde = prog_speed < 0
                        prog_dec = pos_eq[1]
                        prog_ra = pos_eq[0]

                    except Exception as e:
                        self.logger.warning(f"Could not calculate secondary progression for {point_name}: {e}. Skipping.")
                        continue
                elif point_name in ['Ascendant', 'Midheaven', 'ImumCoeli', 'Descendant', 'East_Point', 'Vertex']: # Progress angles
                    # Progressed angles for secondary progressions are calculated by advancing the natal chart's
                    # time and then calculating the angles for that advanced (progressed) chart date and natal location.
                    prog_house_data = self.house_calculator.calculate_houses(
                        natal_lat, natal_lon, ephemeris_date_for_progression, natal_house_system
                    )
                    prog_lon = prog_house_data['angles'].get(point_name)
                    if prog_lon is None:
                        self.logger.warning(f"Could not find progressed {point_name} angle. Skipping.")
                        continue
                    
                    prog_lat = 0.0 # Angles are assumed to be on the ecliptic for longitude calculation
                    prog_speed = 0.0 # Angles do not have independent speed like planets
                    prog_distance = 0.0
                    prog_retrograde = False
                    
                    # Calculate RA/Dec for progressed angles for completeness
                    try:
                        (prog_ra, prog_dec, _) = swe.ecl_to_eq(self._jd_ut, prog_lon, 0.0)
                    except Exception as e:
                        self.logger.warning(f"Could not calculate RA/Dec for progressed angle {point_name}: {e}. Setting to 0.0.")
                        prog_ra, prog_dec = 0.0, 0.0 # Fallback

                else:
                    self.logger.warning(f"Unsupported point for secondary progression: {point_name}. Skipping.")
                    continue

                progressed_positions_with_context[point_name] = self._format_point_data(
                    point_name, prog_lon, prog_speed, prog_lat, prog_ra, prog_dec, prog_distance
                )
        
        elif progression_type == 'solar_arc':
            # Solar Arc Directions: All natal points are advanced by the same degree as the progressed Sun moves.
            # First, calculate the progressed Sun's longitude using the secondary progression rule.
            years_passed = (progression_dt_utc - natal_dt_utc).total_seconds() / (365.25 * 24 * 3600)
            ephemeris_date_for_sun_prog = natal_dt_utc + timedelta(days=years_passed)
            
            # Set swisseph for the Sun's progressed date to find the solar arc.
            self._set_location_and_time(ephemeris_date_for_sun_prog, natal_lat, natal_lon, natal_elevation)
            
            natal_sun_data = natal_points.get('Sun')
            if natal_sun_data is None or 'longitude' not in natal_sun_data:
                raise ValueError("Natal Sun position required for Solar Arc calculations.")
            natal_sun_lon = natal_sun_data['longitude']
            
            # Calculate the Sun's position at the progressed date
            prog_sun_pos_ecl, ret_flags_sun = swe.calc_ut(self._jd_ut, swe.SUN, flags=self._swe_flags)
            if (ret_flags_sun & swe.FLG_ERR):
                raise RuntimeError(f"Failed to calculate progressed Sun for Solar Arc. Swisseph error flags: {ret_flags_sun}.")
            prog_sun_lon = prog_sun_pos_ecl[0] % 360
            
            # Calculate the Solar Arc degree (the distance the Sun has moved in secondary progression)
            solar_arc_degree = (prog_sun_lon - natal_sun_lon + 360) % 360
            self.logger.debug(f"Natal Sun: {natal_sun_lon:.3f}, Prog Sun: {prog_sun_lon:.3f}, Solar Arc Degree: {solar_arc_degree:.3f}")

            # Apply this solar_arc_degree to all chosen natal points
            for point_name in points_to_progress:
                natal_point_data = natal_points.get(point_name)
                if natal_point_data and 'longitude' in natal_point_data:
                    natal_lon_base = natal_point_data['longitude']
                    prog_lon = (natal_lon_base + solar_arc_degree) % 360
                    
                    # For Solar Arc, other parameters (latitude, speed, retrograde, RA, Dec) are typically
                    # inherited from natal and then shifted, not re-calculated via ephemeris from scratch,
                    # as it's a symbolic direction.
                    prog_lat = natal_point_data.get('ecliptic_latitude', 0.0)
                    prog_speed = 0.0 # Solar arc points do not have their own speed in this context
                    prog_distance = natal_point_data.get('distance_au', 0.0)
                    prog_retrograde = False # Only actual planetary motion has retrograde
                    
                    # Calculate RA/Dec for the solar arc directed point using the new longitude and natal latitude
                    try:
                        (prog_ra, prog_dec, _) = swe.ecl_to_eq(self._jd_ut, prog_lon, prog_lat)
                    except Exception as e:
                        self.logger.warning(f"Could not calculate RA/Dec for solar arc directed {point_name}: {e}. Setting to 0.0.")
                        prog_ra, prog_dec = 0.0, 0.0 # Fallback

                    progressed_positions_with_context[point_name] = self._format_point_data(
                        point_name, prog_lon, prog_speed, prog_lat, prog_ra, prog_dec, prog_distance
                    )
                else:
                    self.logger.warning(f"Could not find natal data for {point_name} for Solar Arc. Skipping.")
        else:
            raise ValueError(f"Unsupported progression type: {progression_type}. Choose 'secondary' or 'solar_arc'.")


        progression_aspects = []
        natal_points_for_aspecting_input = {
            name: {'name': natal_points[name]['name'], 'longitude': natal_points[name]['longitude'],
                   'speed': natal_points[name].get('speed', 0.0), 'retrograde': natal_points[name].get('retrograde', False)}
            for name in natal_points.keys() if 'longitude' in natal_points[name] and name not in ['Vertex', 'East_Point']
        }

        progressed_points_for_aspect_input = {
            name: {'name': data['name'], 'longitude': data['longitude'], 'speed': data['speed'], 'retrograde': data['retrograde']}
            for name, data in progressed_positions_with_context.items()
        }

        for prog_name, prog_data in progressed_points_for_aspect_input.items():
            for natal_name, natal_data in natal_points_for_aspecting_input.items():
                diff_abs = abs(prog_data['longitude'] - natal_data['longitude'])
                normalized_diff = diff_abs
                if normalized_diff > 180:
                    normalized_diff = 360 - normalized_diff

                for aspect_def in self.aspect_calculator.aspect_definitions:
                    aspect_name = aspect_def['name']
                    aspect_angle = aspect_def['angle']
                    base_orb = aspect_def['orb'].get('default', 1.0)

                    if (prog_name in LUMINARIES or natal_name in LUMINARIES) and 'luminaries' in aspect_def['orb']:
                        base_orb = aspect_def['orb']['luminaries']

                    if abs(normalized_diff - aspect_angle) <= base_orb:
                        is_applying = False
                        # Applying/Separating for progressions: check if current deviation is less than future deviation
                        # This logic uses the progressed body's calculated speed. For Solar Arc, speed is typically 0,
                        # so applying/separating for Solar Arc is often conceptual (e.g., hit an aspect X months ago).
                        # This implementation correctly reflects the instantaneous speed of the progressed point.
                        prog_lon_future = (prog_data['longitude'] + prog_data['speed']) % 360
                        diff_future = abs(prog_lon_future - natal_data['longitude'])
                        if diff_future > 180: diff_future = 360 - diff_future
                        
                        current_deviation = abs(normalized_diff - aspect_angle)
                        future_deviation = abs(diff_future - aspect_angle)
                        if future_deviation < current_deviation:
                            is_applying = True

                        progression_aspects.append({
                            'progressed_point': prog_name,
                            'natal_point': natal_name,
                            'aspect_type': aspect_name,
                            'angle': aspect_angle,
                            'actual_angle': round(normalized_diff, 3),
                            'orb': round(abs(normalized_diff - aspect_angle), 3),
                            'applying': is_applying,
                            'progressed_longitude': round(prog_data['longitude'], 3),
                            'natal_longitude': round(natal_data['longitude'], 3)
                        })
        self.logger.info(f"Found {len(progression_aspects)} {progression_type} aspects.")

        # Integrate Fixed Stars Progressions (if requested)
        fixed_stars_progression_data = {}
        if include_fixed_stars_progression_aspects:
            # Fixed stars aspecting the *progressed* chart (at the progression date and natal location)
            fixed_stars_progression_data['aspects_to_progressed'] = self._calculate_fixed_star_aspects(
                progressed_positions_with_context, 
                progression_dt_utc,
                natal_lat, natal_lon, natal_elevation, # Location for fixed star calculation
                orb_longitude=1.0, 
                orb_declination_parallel=0.5
            )

        progression_chart_result = {
            'progression_datetime_utc': progression_dt_utc.isoformat(),
            'progression_type': progression_type,
            'progressed_positions': progressed_positions_with_context,
            'progressed_aspects_to_natal': sorted(progression_aspects, key=lambda x: x['orb'])
        }

        if fixed_stars_progression_data:
            progression_chart_result['fixed_stars_progressions'] = fixed_stars_progression_data

        return progression_chart_result

    def calculate_harmonic_chart(self, chart_data: Dict[str, Any], harmonic_number: int) -> Dict[str, Any]:
        """
        Calculates a harmonic chart for the given chart data.
        In a harmonic chart, each planet's longitude is multiplied by the harmonic number,
        and the result is normalized back to 360 degrees.

        Args:
            chart_data (Dict[str, Any]): The natal chart data.
            harmonic_number (int): The harmonic number (e.g., 5 for 5th harmonic, 7 for 7th).

        Returns:
            Dict[str, Any]: A new chart-like dictionary with harmonic positions.
        Raises:
            ValueError: If harmonic_number is not a positive integer.
            RuntimeError: If chart_data is malformed.
        """
        if not isinstance(harmonic_number, int) or harmonic_number <= 0:
            raise ValueError("Harmonic number must be a positive integer.")
        if 'points' not in chart_data or not isinstance(chart_data['points'], dict):
            raise RuntimeError("Malformed chart_data for harmonic calculation: missing 'points'.")

        self.logger.info(f"Calculating {harmonic_number}th harmonic chart.")

        harmonic_points = {}
        for point_name, point_data in chart_data['points'].items():
            if 'longitude' not in point_data or 'error' in point_data:
                continue

            # Only operate on planetary bodies and angles for harmonic charts, not derived points like Arabic parts.
            if point_name not in PLANET_ID_MAP and point_name not in ['Ascendant', 'Midheaven', 'ImumCoeli', 'Descendant', 'Vertex', 'East_Point']:
                continue

            original_lon = point_data['longitude']
            harmonic_lon = (original_lon * harmonic_number) % 360.0

            # Re-format the point with the new harmonic longitude
            # For harmonic charts, other attributes (like speed, retrograde, latitude, RA/Dec)
            # are typically not re-calculated in the harmonic dimension; they are usually ignored
            # or taken as the natal values, or re-derived from harmonic longitude alone.
            harmonic_point_details = self._format_point_data(
                point_name,
                harmonic_lon,
                speed_deg_per_day=0.0, # Derived charts don't have intrinsic speed
                ecliptic_latitude_deg=0.0 # Harmonic charts are typically considered 2D on the ecliptic
            )
            # Harmonic charts typically don't use houses in the same way, or require re-derivation
            # of a harmonic Ascendant/cusps. For basic output, house is set to None.
            harmonic_point_details['house'] = None 
            harmonic_point_details['dignities'] = {"status": "N/A"} # Dignities not typically applied to harmonic positions
            
            harmonic_points[point_name] = harmonic_point_details
        
        # Recalculate aspects for the harmonic chart using the harmonic points
        aspect_input_points = {
            name: {'name': data['name'], 'longitude': data['longitude'], 'retrograde': data.get('retrograde', False), 'speed': data.get('speed', 0.0)}
            for name, data in harmonic_points.items()
            if 'longitude' in data and data['name'] not in {'Vertex', 'East_Point'}
        }
        harmonic_aspects = self.aspect_calculator.find_aspects(aspect_input_points)

        return {
            'metadata': {
                'original_chart_datetime_utc': chart_data['metadata']['datetime_utc'],
                'original_chart_latitude': chart_data['metadata']['latitude'],
                'original_chart_longitude': chart_data['metadata']['longitude'],
                'harmonic_number': harmonic_number,
                'zodiac_type': self.zodiac_type, # Harmonic chart uses the same zodiac type as the original
                'ayanamsa': self.ayanamsa_name if self.zodiac_type == 'sidereal' else None
            },
            'points': harmonic_points,
            'aspects': harmonic_aspects
        }
    
    def calculate_solar_return_chart(self, natal_chart_data: Dict[str, Any], return_year: int) -> Dict[str, Any]:
        """
        Calculates the Solar Return chart for a specific year.
        The Solar Return chart is cast for the exact moment the Sun returns to its natal longitude.

        Args:
            natal_chart_data (Dict[str, Any]): The full natal chart data.
            return_year (int): The calendar year for which to calculate the Solar Return.

        Returns:
            Dict[str, Any]: The calculated Solar Return chart.
        Raises:
            ValueError: If natal data is missing or Sun position cannot be found.
            RuntimeError: If Swisseph calculation for return time fails.
        """
        self.logger.info(f"Calculating Solar Return chart for year {return_year}")

        if 'metadata' not in natal_chart_data or 'points' not in natal_chart_data:
            raise ValueError("Natal chart data is malformed (missing 'metadata' or 'points').")

        natal_sun_lon = natal_chart_data['points'].get('Sun', {}).get('longitude')
        if natal_sun_lon is None:
            raise ValueError("Natal Sun longitude not found in natal chart data.")

        natal_dt_utc = datetime.fromisoformat(natal_chart_data['metadata']['datetime_utc'])
        natal_lat = natal_chart_data['metadata']['latitude']
        natal_lon = natal_chart_data['metadata']['longitude']
        natal_elevation = natal_chart_data['metadata'].get('elevation', 0.0)
        natal_house_system = natal_chart_data['metadata'].get('house_system', 'P')

        # Find the approximate Julian Day for the return. Start from the birthday in the return_year.
        approx_dt_for_return = datetime(return_year, natal_dt_utc.month, natal_dt_utc.day,
                                        natal_dt_utc.hour, natal_dt_utc.minute, natal_dt_utc.second)
        
        # Convert to UTC if approx_dt_for_return is not already (assuming it's natal local time, then adjusted)
        # However, for swisseph, we always work with UTC. So, it should be the UTC equivalent of natal_dt_utc.
        # For Solar Return, the "date" is just a guess to find the correct Julian Day.
        # We need the JD of the natal moment to properly find the return.
        
        # Use swe.solret to find the precise return Julian Day
        # swe.solret(jd_base, geolat, geolon, natal_sun_lon, sid_mode_flag)
        # jd_base should be the natal JD or a JD around the target year.
        
        # Need to establish a base JD that's tropical or sidereal consistent with the natal chart.
        # This requires setting the swe.set_sid_mode correctly BEFORE calling swe.solret.
        # The engine's __init__ already does this.

        jd_approx = swe.julday(approx_dt_for_return.year, approx_dt_for_return.month, approx_dt_for_return.day,
                               approx_dt_for_return.hour + approx_dt_for_return.minute/60 + approx_dt_for_return.second/3600)
        
        try:
            # The returned JD is the exact moment of the Solar Return.
            return_jd = swe.solret(jd_approx, natal_lat, natal_lon, natal_sun_lon, self._swe_flags)
            return_dt_utc = swe.revjul(return_jd)
            # Reconstruct datetime object from tuple (year, month, day, hour, min, sec, weekday)
            solar_return_dt_utc = datetime(
                return_dt_utc[0], return_dt_utc[1], return_dt_utc[2],
                int(return_dt_utc[3]), int((return_dt_utc[3]*60) % 60), int((return_dt_utc[3]*3600) % 60)
            )
        except Exception as e:
            self.logger.error(f"Error calculating Solar Return time for {return_year}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to calculate Solar Return time: {str(e)}")

        # Now, calculate a full chart for this Solar Return moment and natal location
        solar_return_chart = self.calculate_chart(
            dt_utc=solar_return_dt_utc,
            latitude=natal_lat,
            longitude=natal_lon,
            elevation=natal_elevation,
            house_system=natal_house_system,
            points_to_include=DEFAULT_NATAL_POINTS_NAMES,
            include_fixed_stars_positions=False, # Can be set to True by caller
            include_fixed_stars_aspects=False,
            include_arabic_parts=False,
            include_midpoints=False,
            include_antiscia=False
        )
        
        solar_return_chart['metadata']['chart_type'] = 'Solar Return'
        solar_return_chart['metadata']['natal_chart_source'] = natal_chart_data['metadata']['datetime_utc']
        solar_return_chart['metadata']['solar_return_year'] = return_year
        
        return solar_return_chart


    def calculate_lunar_return_chart(self, natal_chart_data: Dict[str, Any], target_dt_utc: datetime) -> Dict[str, Any]:
        """
        Calculates the Lunar Return chart closest to a specific target date.
        The Lunar Return chart is cast for the exact moment the Moon returns to its natal longitude.

        Args:
            natal_chart_data (Dict[str, Any]): The full natal chart data.
            target_dt_utc (datetime): The UTC date/time around which to find the closest Lunar Return.

        Returns:
            Dict[str, Any]: The calculated Lunar Return chart.
        Raises:
            ValueError: If natal data is missing or Moon position cannot be found.
            RuntimeError: If Swisseph calculation for return time fails.
        """
        self.logger.info(f"Calculating Lunar Return chart closest to {target_dt_utc}")

        if 'metadata' not in natal_chart_data or 'points' not in natal_chart_data:
            raise ValueError("Natal chart data is malformed (missing 'metadata' or 'points').")

        natal_moon_lon = natal_chart_data['points'].get('Moon', {}).get('longitude')
        if natal_moon_lon is None:
            raise ValueError("Natal Moon longitude not found in natal chart data.")

        natal_lat = natal_chart_data['metadata']['latitude']
        natal_lon = natal_chart_data['metadata']['longitude']
        natal_elevation = natal_chart_data['metadata'].get('elevation', 0.0)
        natal_house_system = natal_chart_data['metadata'].get('house_system', 'P')

        # Use swe.lunret to find the precise return Julian Day
        # swe.lunret(jd_base, geolat, geolon, natal_moon_lon, sid_mode_flag)
        jd_approx = swe.julday(target_dt_utc.year, target_dt_utc.month, target_dt_utc.day,
                               target_dt_utc.hour + target_dt_utc.minute/60 + target_dt_utc.second/3600)
        
        try:
            return_jd = swe.lunret(jd_approx, natal_lat, natal_lon, natal_moon_lon, self._swe_flags)
            return_dt_utc_tuple = swe.revjul(return_jd)
            lunar_return_dt_utc = datetime(
                return_dt_utc_tuple[0], return_dt_utc_tuple[1], return_dt_utc_tuple[2],
                int(return_dt_utc_tuple[3]), int((return_dt_utc_tuple[3]*60) % 60), int((return_dt_utc_tuple[3]*3600) % 60)
            )
        except Exception as e:
            self.logger.error(f"Error calculating Lunar Return time for {target_dt_utc}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to calculate Lunar Return time: {str(e)}")

        # Calculate a full chart for this Lunar Return moment and natal location
        lunar_return_chart = self.calculate_chart(
            dt_utc=lunar_return_dt_utc,
            latitude=natal_lat,
            longitude=natal_lon,
            elevation=natal_elevation,
            house_system=natal_house_system,
            points_to_include=DEFAULT_NATAL_POINTS_NAMES,
            include_fixed_stars_positions=False, # Can be set to True by caller
            include_fixed_stars_aspects=False,
            include_arabic_parts=False,
            include_midpoints=False,
            include_antiscia=False
        )
        
        lunar_return_chart['metadata']['chart_type'] = 'Lunar Return'
        lunar_return_chart['metadata']['natal_chart_source'] = natal_chart_data['metadata']['datetime_utc']
        lunar_return_chart['metadata']['lunar_return_closest_to'] = target_dt_utc.isoformat()

        return lunar_return_chart

    def calculate_synastry_aspects(self, chart1_data: Dict[str, Any], chart2_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculates synastry aspects (inter-chart aspects) between points of two natal charts.

        Args:
            chart1_data (Dict[str, Any]): The first natal chart data.
            chart2_data (Dict[str, Any]): The second natal chart data.

        Returns:
            List[Dict[str, Any]]: A list of aspects between points of chart1 and chart2.
        Raises:
            ValueError: If chart data is malformed.
        """
        self.logger.info("Calculating synastry aspects between two charts.")

        if 'points' not in chart1_data or 'points' not in chart2_data:
            raise ValueError("Both chart data inputs must contain a 'points' key.")
        
        chart1_points = chart1_data['points']
        chart2_points = chart2_data['points']

        synastry_aspects = []

        # Prepare points for aspect calculation, filtering out non-planet/angle points
        points1_for_aspecting = {
            name: {'name': data['name'], 'longitude': data['longitude'], 'speed': data.get('speed', 0.0)}
            for name, data in chart1_points.items()
            if 'longitude' in data and data['name'] in PLANET_ID_MAP or data['name'] in ['Ascendant', 'Midheaven', 'ImumCoeli', 'Descendant']
        }
        points2_for_aspecting = {
            name: {'name': data['name'], 'longitude': data['longitude'], 'speed': data.get('speed', 0.0)}
            for name, data in chart2_points.items()
            if 'longitude' in data and data['name'] in PLANET_ID_MAP or data['name'] in ['Ascendant', 'Midheaven', 'ImumCoeli', 'Descendant']
        }

        for p1_name, p1_data in points1_for_aspecting.items():
            for p2_name, p2_data in points2_for_aspecting.items():
                lon1 = p1_data['longitude']
                lon2 = p2_data['longitude']

                diff_abs = abs(lon1 - lon2)
                normalized_diff = diff_abs
                if normalized_diff > 180:
                    normalized_diff = 360 - normalized_diff

                for aspect_def in self.aspect_calculator.aspect_definitions:
                    aspect_name = aspect_def['name']
                    aspect_angle = aspect_def['angle']
                    base_orb = aspect_def['orb'].get('default', 1.0)

                    # Apply luminaries orb if either point is a luminary
                    if (p1_name in LUMINARIES or p2_name in LUMINARIES) and 'luminaries' in aspect_def['orb']:
                        base_orb = aspect_def['orb']['luminaries']

                    if abs(normalized_diff - aspect_angle) <= base_orb:
                        synastry_aspects.append({
                            'chart1_point': p1_name,
                            'chart2_point': p2_name,
                            'aspect_type': aspect_name,
                            'angle': aspect_angle,
                            'actual_angle': round(normalized_diff, 3),
                            'orb': round(abs(normalized_diff - aspect_angle), 3),
                            # For synastry, applying/separating is not typically calculated as charts are static
                            'chart1_longitude': round(lon1, 3),
                            'chart2_longitude': round(lon2, 3)
                        })
        self.logger.info(f"Found {len(synastry_aspects)} synastry aspects.")
        return sorted(synastry_aspects, key=lambda x: x['orb'])

    def calculate_composite_chart(self, chart1_data: Dict[str, Any], chart2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a Composite Chart between two natal charts.
        A composite chart is a single chart derived from the midpoints of corresponding planets/points
        of two individuals.

        Args:
            chart1_data (Dict[str, Any]): The first natal chart data.
            chart2_data (Dict[str, Any]): The second natal chart data.

        Returns:
            Dict[str, Any]: The calculated composite chart data.
        Raises:
            ValueError: If chart data is malformed.
        """
        self.logger.info("Calculating Composite Chart between two natal charts.")

        if 'points' not in chart1_data or 'points' not in chart2_data:
            raise ValueError("Both chart data inputs must contain a 'points' key.")

        composite_points = {}
        
        # Calculate midpoints for each corresponding planet/point
        for point_name in PLANET_ID_MAP.keys(): # Only composite traditional planets + nodes
            p1_data = chart1_data['points'].get(point_name)
            p2_data = chart2_data['points'].get(point_name)

            if p1_data and p2_data and 'longitude' in p1_data and 'longitude' in p2_data:
                lon1 = p1_data['longitude']
                lon2 = p2_data['longitude']

                # Composite midpoint (shortest arc)
                midpoint_lon_raw = (lon1 + lon2) / 2.0
                diff = abs(lon1 - lon2)
                if diff > 180:
                    composite_lon = (midpoint_lon_raw + 180) % 360
                else:
                    composite_lon = midpoint_lon_raw
                composite_lon %= 360

                # Composite charts do not have intrinsic speed or latitude from midpointing alone.
                # Ecliptic latitude is often taken as the midpoint of latitudes, or ignored.
                # For simplicity, set to 0.0 for now, as it's a derived, theoretical chart.
                composite_point_details = self._format_point_data(
                    point_name, composite_lon, speed_deg_per_day=0.0, ecliptic_latitude_deg=0.0
                )
                composite_points[point_name] = composite_point_details

        # Calculate composite Ascendant and MC (using midpoint of natal Asc/MC)
        # This requires their original longitudes from natal charts
        natal1_asc = chart1_data['houses']['angles'].get('Ascendant')
        natal2_asc = chart2_data['houses']['angles'].get('Ascendant')
        natal1_mc = chart1_data['houses']['angles'].get('Midheaven')
        natal2_mc = chart2_data['houses']['angles'].get('Midheaven')

        if natal1_asc is not None and natal2_asc is not None:
            comp_asc_lon = ((natal1_asc + natal2_asc) / 2.0) % 360
            if abs(natal1_asc - natal2_asc) > 180: comp_asc_lon = (comp_asc_lon + 180) % 360
            
            asc_details = self._format_point_data('Ascendant', comp_asc_lon, speed_deg_per_day=0.0, ecliptic_latitude_deg=0.0)
            asc_details['house'] = 1 # Composite Ascendant is the 1st house cusp
            composite_points['Ascendant'] = asc_details

        if natal1_mc is not None and natal2_mc is not None:
            comp_mc_lon = ((natal1_mc + natal2_mc) / 2.0) % 360
            if abs(natal1_mc - natal2_mc) > 180: comp_mc_lon = (comp_mc_lon + 180) % 360
            
            mc_details = self._format_point_data('Midheaven', comp_mc_lon, speed_deg_per_day=0.0, ecliptic_latitude_deg=0.0)
            mc_details['house'] = 10 # Composite MC is the 10th house cusp
            composite_points['Midheaven'] = mc_details
        
        # Recalculate aspects for the composite chart
        aspect_input_points = {
            name: {'name': data['name'], 'longitude': data['longitude'], 'retrograde': data.get('retrograde', False), 'speed': data.get('speed', 0.0)}
            for name, data in composite_points.items()
            if 'longitude' in data and data['name'] not in {'Vertex', 'East_Point'}
        }
        composite_aspects = self.aspect_calculator.find_aspects(aspect_input_points)

        # For houses, the composite Ascendant and MC define the axis, but cusps for other houses
        # are not typically calculated via midpointing other natal cusps.
        # A common practice is to use a "House of Houses" system or derive from the composite Ascendant.
        # For simplicity, we can list the Composite Ascendant and MC as the primary angles.
        # Other cusps would need a new House Calculation using the composite Ascendant as the 1st cusp.
        # This is a simplification. For truly robust composite charts, one might compute an averaged location/time
        # or use specific software implementations for composite houses.
        composite_houses_data = {
            "cusps": [], # Can be derived if a full house system is applied starting from composite Asc
            "angles": {name: p['longitude'] for name, p in composite_points.items() if name in ['Ascendant', 'Midheaven']}
        }

        # Analyze composite chart signature
        composite_chart_signature = self._analyze_chart_signature(composite_points)

        return {
            'metadata': {
                'chart_type': 'Composite Chart',
                'chart1_source': chart1_data['metadata']['datetime_utc'],
                'chart2_source': chart2_data['metadata']['datetime_utc'],
                'zodiac_type': self.zodiac_type, # Composite chart uses the same zodiac type as the originals
                'ayanamsa': self.ayanamsa_name if self.zodiac_type == 'sidereal' else None
            },
            'points': composite_points,
            'aspects': composite_aspects,
            'houses': composite_houses_data,
            'chart_signature': composite_chart_signature
        }

    def get_daily_horoscope_data(self, sign_key: str, target_date_utc: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Calculates the raw astrological data points relevant for a daily horoscope for a given zodiac sign.
        This method provides **astrological data**, not textual interpretations.

        Args:
            sign_key (str): The key of the zodiac sign (e.g., 'aries', 'taurus').
            target_date_utc (Optional[datetime]): The UTC date for which to generate the horoscope data.
                                                 If None, uses the current UTC datetime.

        Returns:
            Dict[str, Any]: A dictionary containing relevant astrological data points.
                            This data can then be used by an external content service for interpretation.
        Raises:
            RuntimeError: If underlying calculations fail.
            ValueError: If the zodiac_sign_key is invalid.
        """
        target_dt = target_date_utc or datetime.utcnow()

        # Ensure zodiac sign key is valid based on internal ZODIAC_SIGNS
        sign_key_lower = sign_key.lower()
        if sign_key_lower not in [s.lower() for s in ZODIAC_SIGNS]:
            raise ValueError(f"Invalid zodiac sign key: {sign_key}. Must be one of: {ZODIAC_SIGNS}")
        
        sign_display_name = next((s for s in ZODIAC_SIGNS if s.lower() == sign_key_lower), "Unknown")

        # Get transiting planet positions for the target date.
        # For a general daily horoscope, location is typically ignored (geocentric positions),
        # as it's a broad-strokes forecast not tied to specific observer's houses.
        # This will not set topocentric flags unless _set_location_and_time is used to do so.
        jd_ut_for_horoscope = swe.julday(target_dt.year, target_dt.month, target_dt.day,
                                        target_dt.hour + target_dt.minute/60 + target_dt.second/3600)
        
        # Ensure geocentric calculation for general horoscope.
        # Reset topocentric settings if they were set globally.
        swe.set_topo(0, 0, 0)
        current_swe_flags = swe.FLG_SWIEPH | swe.FLG_SPEED # No FLG_TOPOCTR for general horoscope

        # Fetch transiting points using the neutral geocentric setup
        transiting_points_raw = {}
        for planet_name in DEFAULT_NATAL_POINTS_NAMES: # Fetch all default natal points
            swe_id = PLANET_ID_MAP.get(planet_name)
            if swe_id is not None:
                try:
                    pos_ecl, ret_flags_ecl = swe.calc_ut(jd_ut_for_horoscope, swe_id, flags=current_swe_flags)
                    pos_eq, ret_flags_eq = swe.calc_ut(jd_ut_for_horoscope, swe_id, flags=current_swe_flags | swe.FLG_EQUATORIAL)
                    if (ret_flags_ecl & swe.FLG_ERR) or (ret_flags_eq & swe.FLG_ERR):
                         self.logger.warning(f"Error getting {planet_name} for horoscope: {ret_flags_ecl}/{ret_flags_eq}")
                         continue
                    transiting_points_raw[planet_name] = {
                        'name': planet_name,
                        'longitude': pos_ecl[0] % 360,
                        'ecliptic_latitude': pos_ecl[1],
                        'declination': pos_eq[1],
                        'speed': pos_ecl[3],
                        'retrograde': pos_ecl[3] < 0,
                        'right_ascension': pos_eq[0],
                        'distance_au': pos_ecl[2]
                    }
                except Exception as e:
                    self.logger.error(f"Error calculating {planet_name} for daily horoscope: {e}", exc_info=True)
            
        transiting_points_with_context = {}
        for name, data in transiting_points_raw.items():
            sign_info = self.house_calculator.get_sign_and_degree(data['longitude'])
            transiting_points_with_context[name] = {
                'name': name,
                'longitude': round(data['longitude'], 3),
                'sign_name': sign_info['sign_name'],
                'degree_in_sign': sign_info['degree_in_sign'],
                'minute_in_sign': sign_info['minute_in_sign'],
                'second_in_sign': sign_info['second_in_sign'],
                'retrograde': data['retrograde'],
                'speed': round(data['speed'], 3)
            }

        # Get Moon phase for the target date
        moon_phase_data = self.get_moon_phase(dt_utc=target_dt)

        horoscope_data = {
            "date": target_dt.isoformat(),
            "sign_key": sign_key_lower,
            "sign_name": sign_display_name,
            "transiting_planets_data": transiting_points_with_context, # Detailed transiting planet data
            "moon_phase_data": moon_phase_data, # Detailed moon phase data
        }
        return horoscope_data


    def get_moon_phase(self, dt_utc: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculates moon phase details for a given UTC datetime."""
        target_dt = dt_utc or datetime.utcnow() # Use datetime.utcnow() if no specific dt_utc is provided.

        if not self.ephemeris_manager.is_initialized(): 
            self.logger.error("AstrologyEngine: EphemerisManager not initialized for moon phase calculation.")
            raise RuntimeError("Ephemeris not initialized for moon phase calculation.")

        jd = swe.julday(target_dt.year, target_dt.month, target_dt.day,
                        target_dt.hour + target_dt.minute/60 + target_dt.second/3600)
        pos_flags = swe.FLG_SWIEPH # Geocentric calculation for moon phase is standard

        # Temporarily unset topocentric settings if they were active, for geocentric moon phase calc
        swe.set_topo(0,0,0)
        
        sun_calc, sun_err = swe.calc_ut(jd, swe.SUN, pos_flags)
        if sun_err and sun_err.strip().startswith('-'): 
            raise RuntimeError(f"Could not get Sun position for moon phase: {sun_err.strip()}")
        if not sun_calc or len(sun_calc) == 0: 
            raise RuntimeError("Could not get Sun position (None or empty array returned).")
        sun_lon = sun_calc[0]

        moon_calc, moon_err = swe.calc_ut(jd, swe.MOON, pos_flags)
        if moon_err and moon_err.strip().startswith('-'): 
            raise RuntimeError(f"Could not get Moon position for moon phase: {moon_err.strip()}")
        if not moon_calc or len(moon_calc) == 0: 
            raise RuntimeError("Could not get Moon position (None or empty array returned).")
        moon_lon = moon_calc[0]
        
        # Restore original topocentric settings after moon phase calculation if they were set globally.
        swe.set_topo(self._current_location["longitude"], self._current_location["latitude"], self._current_location["elevation"])

        elongation = (moon_lon - sun_lon + 360) % 360
        phase_name = self._determine_moon_phase_name(elongation)
        
        # Calculate illumination percentage (standard astronomical formula for phase angle)
        # Phase angle (i) is related to elongation (E) by i = 180 - E. Or more precisely, for lunar phase,
        # it's 0 at new moon, 180 at full moon.
        # Illumination percentage (k) = (1 + cos(i)) / 2 * 100
        # If elongation is E, then phase angle is abs(E - 180) for astronomical purposes.
        # Astrologically, elongation is used directly.
        # Astronomical formula for illumination is (1 + cos(elongation_from_full_moon_in_radians)) / 2
        # where elongation_from_full_moon_in_radians is angle from opposition (180 deg).
        illumination_formula_angle = abs(elongation - 180) # Angle from full moon for illumination calc
        illumination = (1 + math.cos(math.radians(illumination_formula_angle))) / 2.0 * 100.0


        return {
            "datetime_utc": target_dt.isoformat(), 
            "julian_day_utc": jd,
            "sun_longitude": round(sun_lon, 4), 
            "moon_longitude": round(moon_lon, 4),
            "elongation_degrees": round(elongation, 2),
            "illumination_percent": round(illumination, 1),
            "phase_name": phase_name,
            "is_waxing": 0 < elongation < 180, 
            "is_waning": 180 < elongation < 360, 
        }

    def _determine_moon_phase_name(self, elongation: float) -> str:
        """Determines the astrological moon phase name from elongation in degrees."""
        if 0 <= elongation < 22.5 or elongation >= 337.5: return "New Moon" 
        elif 22.5 <= elongation < 67.5: return "Waxing Crescent"
        elif 67.5 <= elongation < 112.5: return "First Quarter"
        elif 112.5 <= elongation < 157.5: return "Waxing Gibbous"
        elif 157.5 <= elongation < 202.5: return "Full Moon"
        elif 202.5 <= elongation < 247.5: return "Waning Gibbous"
        elif 247.5 <= elongation < 292.5: return "Last Quarter" 
        elif 292.5 <= elongation < 337.5: return "Waning Crescent"
        return "Unknown Phase" 

# --- Service Interface Functions (wrappers to use AstrologyEngine) ---
# These functions act as convenient entry points to initialize and use the AstrologyEngine.
# They convert input formats (e.g., strings) to those required by AstrologyEngine.
# They are not part of AstrologyEngine class itself but demonstrate how to use it
# as a self-contained module.

def get_natal_chart_details_service(
    birth_datetime_str: str, birth_timezone_offset_hours: float, # Use offset for simplicity
    latitude: float, longitude: float, altitude: float = 0, 
    house_system_name: str = "Placidus",
    zodiac_type: str = 'tropical',
    ayanamsa_name: str = 'Fagan-Bradley',
    include_fixed_stars_positions: bool = False,
    include_fixed_stars_aspects: bool = False,
    include_arabic_parts: bool = False,
    include_midpoints: bool = False,
    include_antiscia: bool = False,
    midpoint_orb: float = 1.0
    ) -> Dict[str, Any]:
    """
    Service wrapper to calculate a natal chart using AstrologyEngine.

    Args:
        birth_datetime_str (str): Local birth datetime string (e.g., "1990-05-15T14:30:00").
                                  Assumes ISO 8601 format.
        birth_timezone_offset_hours (float): Timezone offset from UTC in hours (e.g., -5.0 for EST).
        latitude (float): Birth latitude.
        longitude (float): Birth longitude.
        altitude (float): Birth altitude in meters.
        house_system_name (str): Name of the house system.
        zodiac_type (str): 'tropical' or 'sidereal'.
        ayanamsa_name (str): Ayanamsa name if sidereal zodiac is used.
        include_fixed_stars_positions (bool): If True, includes general fixed star positions.
        include_fixed_stars_aspects (bool): If True, includes fixed star aspects to natal points.
        include_arabic_parts (bool): If True, includes a selection of Arabic Parts.
        include_midpoints (bool): If True, calculates and includes midpoints.
        include_antiscia (bool): If True, calculates and includes antiscia and contra-antiscia.
        midpoint_orb (float): Orb for midpoint calculations.

    Returns:
        Dict[str, Any]: Full natal chart data or an error message.
    """
    _logger = logging.getLogger(__name__) # Use module logger for this service wrapper
    try:
        # Convert local datetime string and offset to UTC datetime object
        dt_local = datetime.fromisoformat(birth_datetime_str)
        dt_utc = dt_local - timedelta(hours=birth_timezone_offset_hours)
        
        # Ensure the datetime object is timezone-naive UTC for swisseph
        dt_utc_naive = dt_utc.replace(tzinfo=None)

        engine = AstrologyEngine(ephemeris_path="ephemeris_data", zodiac_type=zodiac_type, ayanamsa_name=ayanamsa_name)
        
        # Convert house system name to code
        house_system_code = HOUSE_SYSTEM_CHAR_CODES.get(house_system_name, house_system_name)
        if len(house_system_code) != 1:
            return {"error": f"Invalid house_system_name: {house_system_name}. Must be a recognized name or a single character code."}

        full_chart_output = engine.calculate_chart(
            dt_utc=dt_utc_naive,
            latitude=latitude,
            longitude=longitude,
            elevation=altitude, # Renamed `altitude` to `elevation` for consistency with Swisseph terminology
            house_system=house_system_code,
            points_to_include=DEFAULT_NATAL_POINTS_NAMES, # Can be customized
            include_fixed_stars_positions=include_fixed_stars_positions,
            include_fixed_stars_aspects=include_fixed_stars_aspects,
            include_arabic_parts=include_arabic_parts,
            include_midpoints=include_midpoints,
            include_antiscia=include_antiscia,
            midpoint_orb=midpoint_orb
        )
        
        if "error" in full_chart_output:
            return {"error": f"AstrologyEngine calculation error: {full_chart_output['error']}"}

        # Add input details for context
        full_chart_output["birth_data_input"] = {
            "datetime_local_str": birth_datetime_str, 
            "timezone_offset_hours": birth_timezone_offset_hours,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "house_system_name_used": house_system_name,
            "datetime_utc_calculated": dt_utc_naive.isoformat(), 
        }
        return full_chart_output
    except Exception as e:
        _logger.error(f"Error in get_natal_chart_details_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred: {str(e)}"}

def get_daily_horoscope_data_service(zodiac_sign_key: str, target_date_utc_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Service wrapper to get raw astrological data for a daily horoscope.
    This provides astrological data, not interpretations.

    Args:
        zodiac_sign_key (str): Key for the zodiac sign (e.g., 'aries').
        target_date_utc_str (Optional[str]): UTC date string (YYYY-MM-DD). If None, uses current UTC date.

    Returns:
        Dict[str, Any]: Astrological data for the daily horoscope or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        target_dt_utc: datetime
        if target_date_utc_str:
            try:
                # Convert date string to datetime, assuming start of day UTC
                target_dt_utc = datetime.strptime(target_date_utc_str, "%Y-%m-%d").replace(hour=12) # Use noon for better daily average
            except ValueError:
                return {"error": "Invalid target_date_utc_str format. Use YYYY-MM-DD."}
        else: 
            target_dt_utc = datetime.utcnow() # Current UTC datetime
            
        engine = AstrologyEngine(ephemeris_path="ephemeris_data") # Default tropical zodiac for horoscopes
        horoscope_data = engine.get_daily_horoscope_data(zodiac_sign_key, target_dt_utc) 
        
        if "error" in horoscope_data:
            return {"error": f"AstrologyEngine calculation error for daily horoscope: {horoscope_data['error']}"}
        
        return horoscope_data

    except Exception as e:
        _logger.error(f"Error in get_daily_horoscope_data_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during daily horoscope data retrieval: {str(e)}"}

def get_moon_phase_service(datetime_utc_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Service wrapper to calculate moon phase details.

    Args:
        datetime_utc_str (Optional[str]): UTC datetime string (ISO 8601). If None, uses current UTC datetime.

    Returns:
        Dict[str, Any]: Moon phase details or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        target_dt_utc: datetime
        if datetime_utc_str:
            try:
                target_dt_utc = datetime.fromisoformat(datetime_utc_str)
            except ValueError:
                return {"error": "Invalid datetime_utc_str format. Use ISO 8601."}
        else: 
            target_dt_utc = datetime.utcnow() # Current UTC datetime
            
        engine = AstrologyEngine(ephemeris_path="ephemeris_data") # Initialize engine (location irrelevant for moon phase)
        moon_phase_data = engine.get_moon_phase(target_dt_utc) 
        
        if "error" in moon_phase_data:
            return {"error": f"AstrologyEngine calculation error for moon phase: {moon_phase_data['error']}"}

        return moon_phase_data
    except Exception as e:
        _logger.error(f"Error in get_moon_phase_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during moon phase calculation: {str(e)}"}

def get_transits_service(
    natal_chart_data: Dict[str, Any],
    transit_datetime_utc_str: str, transit_latitude: float, transit_longitude: float, elevation: float = 0.0,
    transiting_points_to_include: Optional[List[str]] = None,
    natal_points_to_aspect: Optional[List[str]] = None,
    include_fixed_stars_transit_aspects: bool = False
    ) -> Dict[str, Any]:
    """
    Service wrapper to calculate transits.

    Args:
        natal_chart_data (Dict[str, Any]): Full natal chart data.
        transit_datetime_utc_str (str): UTC datetime string for transits (ISO 8601).
        transit_latitude (float): Observer's latitude for transits.
        transit_longitude (float): Observer's longitude for transits.
        elevation (float): Observer's elevation for transits.
        transiting_points_to_include (List[str], optional): Specific transiting points to include.
        natal_points_to_aspect (List[str], optional): Specific natal points to aspect.
        include_fixed_stars_transit_aspects (bool): Include fixed star transits.

    Returns:
        Dict[str, Any]: Transit data or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        transit_dt_utc = datetime.fromisoformat(transit_datetime_utc_str)
        engine = AstrologyEngine(ephemeris_path="ephemeris_data", 
                                 zodiac_type=natal_chart_data['metadata'].get('zodiac_type', 'tropical'),
                                 ayanamsa_name=natal_chart_data['metadata'].get('ayanamsa', 'Fagan-Bradley')) # Ensure consistent zodiac
        transits_data = engine.calculate_transits(
            natal_chart_data=natal_chart_data,
            transit_dt_utc=transit_dt_utc,
            transit_latitude=transit_latitude,
            transit_longitude=transit_longitude,
            elevation=elevation,
            transiting_points_to_include=transiting_points_to_include,
            natal_points_to_aspect=natal_points_to_aspect,
            include_fixed_stars_transit_aspects=include_fixed_stars_transit_aspects
        )
        return transits_data
    except Exception as e:
        _logger.error(f"Error in get_transits_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during transit calculation: {str(e)}"}

def get_progressions_service(
    natal_chart_data: Dict[str, Any],
    progression_datetime_utc_str: str,
    progression_type: str = 'secondary',
    points_to_progress: Optional[List[str]] = None,
    include_fixed_stars_progression_aspects: bool = False
    ) -> Dict[str, Any]:
    """
    Service wrapper to calculate progressions (secondary or solar arc).

    Args:
        natal_chart_data (Dict[str, Any]): Full natal chart data.
        progression_datetime_utc_str (str): UTC datetime string for progression (ISO 8601).
        progression_type (str): 'secondary' or 'solar_arc'.
        points_to_progress (List[str], optional): Specific points to progress.
        include_fixed_stars_progression_aspects (bool): Include fixed star progressions.

    Returns:
        Dict[str, Any]: Progression data or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        progression_dt_utc = datetime.fromisoformat(progression_datetime_utc_str)
        engine = AstrologyEngine(ephemeris_path="ephemeris_data", 
                                 zodiac_type=natal_chart_data['metadata'].get('zodiac_type', 'tropical'),
                                 ayanamsa_name=natal_chart_data['metadata'].get('ayanamsa', 'Fagan-Bradley')) # Ensure consistent zodiac
        progressions_data = engine.calculate_progressions(
            natal_chart_data=natal_chart_data,
            progression_dt_utc=progression_dt_utc,
            progression_type=progression_type,
            points_to_progress=points_to_progress,
            include_fixed_stars_progression_aspects=include_fixed_stars_progression_aspects
        )
        return progressions_data
    except Exception as e:
        _logger.error(f"Error in get_progressions_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during progression calculation: {str(e)}"}

def get_harmonic_chart_service(natal_chart_data: Dict[str, Any], harmonic_number: int) -> Dict[str, Any]:
    """
    Service wrapper to calculate a harmonic chart.

    Args:
        natal_chart_data (Dict[str, Any]): Full natal chart data.
        harmonic_number (int): The harmonic number.

    Returns:
        Dict[str, Any]: Harmonic chart data or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        engine = AstrologyEngine(ephemeris_path="ephemeris_data", 
                                 zodiac_type=natal_chart_data['metadata'].get('zodiac_type', 'tropical'),
                                 ayanamsa_name=natal_chart_data['metadata'].get('ayanamsa', 'Fagan-Bradley')) # Ensure consistent zodiac
        harmonic_chart_data = engine.calculate_harmonic_chart(natal_chart_data, harmonic_number)
        return harmonic_chart_data
    except Exception as e:
        _logger.error(f"Error in get_harmonic_chart_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during harmonic chart calculation: {str(e)}"}

def get_midpoints_service(natal_chart_data: Dict[str, Any], midpoint_orb: float = 1.0) -> Dict[str, Any]:
    """
    Service wrapper to calculate midpoints and their hits for a natal chart.

    Args:
        natal_chart_data (Dict[str, Any]): Full natal chart data.
        midpoint_orb (float): Orb for midpoint "hits" calculation.

    Returns:
        Dict[str, Any]: Midpoint data including 'midpoints' and 'midpoint_hits' or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        engine = AstrologyEngine(ephemeris_path="ephemeris_data")
        if 'points' not in natal_chart_data:
            return {"error": "Natal chart data missing 'points' for midpoint calculation."}
        
        midpoints = engine.calculate_midpoints(natal_chart_data['points'])
        midpoint_hits = engine._find_midpoint_aspects(natal_chart_data['points'], midpoints, midpoint_orb)

        return {"midpoints": midpoints, "midpoint_hits": midpoint_hits}
    except Exception as e:
        _logger.error(f"Error in get_midpoints_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during midpoint calculation: {str(e)}"}

def get_antiscia_service(natal_chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Service wrapper to calculate Antiscia and Contra-Antiscia for a natal chart.

    Args:
        natal_chart_data (Dict[str, Any]): Full natal chart data.

    Returns:
        Dict[str, Any]: Antiscia/Contra-Antiscia data or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        engine = AstrologyEngine(ephemeris_path="ephemeris_data")
        if 'points' not in natal_chart_data or 'metadata' not in natal_chart_data:
             return {"error": "Natal chart data missing 'points' or 'metadata' for antiscia calculation."}
        
        # We need the JD from the original chart for RA/Dec calculations of Antiscia points.
        # This assumes calculate_chart was run and stored the JD.
        # Alternatively, recalculate it here. For robustness, get JD from metadata.
        natal_dt_utc = datetime.fromisoformat(natal_chart_data['metadata']['datetime_utc'])
        # Temporarily set engine's JD and location to that of the natal chart
        engine._set_location_and_time(
            natal_dt_utc, 
            natal_chart_data['metadata']['latitude'], 
            natal_chart_data['metadata']['longitude'], 
            natal_chart_data['metadata'].get('elevation', 0.0)
        )
        
        antiscia_data = engine.calculate_antiscia_points(natal_chart_data['points'])
        return antiscia_data
    except Exception as e:
        _logger.error(f"Error in get_antiscia_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during antiscia calculation: {str(e)}"}

def get_arabic_parts_service(natal_chart_data: Dict[str, Any], part_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Service wrapper to calculate specific Arabic Parts for a natal chart.

    Args:
        natal_chart_data (Dict[str, Any]): Full natal chart data.
        part_names (Optional[List[str]]): List of Arabic Part names to calculate. If None, calculates all hardcoded.

    Returns:
        Dict[str, Any]: Dictionary containing calculated Arabic Parts or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        engine = AstrologyEngine(ephemeris_path="ephemeris_data")
        if 'points' not in natal_chart_data or 'houses' not in natal_chart_data:
            return {"error": "Natal chart data missing 'points' or 'houses' for Arabic Parts calculation."}

        calculated_parts = []
        parts_to_calc = part_names if part_names is not None else list(ARABIC_PARTS_FORMULAS.keys())

        # For _calculate_arabic_part_position, we need the angles as a separate dictionary
        angles = natal_chart_data['houses'].get('angles', {})

        # Temporarily set engine's JD and location to that of the natal chart for accurate part calculation
        natal_dt_utc = datetime.fromisoformat(natal_chart_data['metadata']['datetime_utc'])
        engine._set_location_and_time(
            natal_dt_utc, 
            natal_chart_data['metadata']['latitude'], 
            natal_chart_data['metadata']['longitude'], 
            natal_chart_data['metadata'].get('elevation', 0.0)
        )
        # To determine day/night for specific parts, we need sun's house from the *natal* chart context
        engine._last_calculated_chart_data = natal_chart_data # Mocking the internal state for _calculate_arabic_part_position to get sun's house

        for part_name in parts_to_calc:
            part_data = engine._calculate_arabic_part_position(
                part_name, 
                natal_chart_data['points'], # Pass all points for formula lookup
                angles
            )
            if "error" not in part_data:
                calculated_parts.append(part_data)
            else:
                _logger.warning(f"Failed to calculate {part_name}: {part_data['error']}")
                calculated_parts.append({"name": part_name, "error": part_data['error']})
        
        return {"arabic_parts": calculated_parts}
    except Exception as e:
        _logger.error(f"Error in get_arabic_parts_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during Arabic Parts calculation: {str(e)}"}


def get_solar_return_chart_service(natal_chart_data: Dict[str, Any], return_year: int) -> Dict[str, Any]:
    """
    Service wrapper to calculate a Solar Return chart.

    Args:
        natal_chart_data (Dict[str, Any]): Full natal chart data.
        return_year (int): The calendar year for the Solar Return.

    Returns:
        Dict[str, Any]: Solar Return chart data or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        engine = AstrologyEngine(ephemeris_path="ephemeris_data", 
                                 zodiac_type=natal_chart_data['metadata'].get('zodiac_type', 'tropical'),
                                 ayanamsa_name=natal_chart_data['metadata'].get('ayanamsa', 'Fagan-Bradley'))
        solar_return_chart = engine.calculate_solar_return_chart(natal_chart_data, return_year)
        return solar_return_chart
    except Exception as e:
        _logger.error(f"Error in get_solar_return_chart_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during Solar Return chart calculation: {str(e)}"}

def get_lunar_return_chart_service(natal_chart_data: Dict[str, Any], target_datetime_utc_str: str) -> Dict[str, Any]:
    """
    Service wrapper to calculate a Lunar Return chart.

    Args:
        natal_chart_data (Dict[str, Any]): Full natal chart data.
        target_datetime_utc_str (str): UTC datetime string to find the closest Lunar Return.

    Returns:
        Dict[str, Any]: Lunar Return chart data or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        target_dt_utc = datetime.fromisoformat(target_datetime_utc_str)
        engine = AstrologyEngine(ephemeris_path="ephemeris_data",
                                 zodiac_type=natal_chart_data['metadata'].get('zodiac_type', 'tropical'),
                                 ayanamsa_name=natal_chart_data['metadata'].get('ayanamsa', 'Fagan-Bradley'))
        lunar_return_chart = engine.calculate_lunar_return_chart(natal_chart_data, target_dt_utc)
        return lunar_return_chart
    except Exception as e:
        _logger.error(f"Error in get_lunar_return_chart_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during Lunar Return chart calculation: {str(e)}"}

def get_synastry_aspects_service(chart1_data: Dict[str, Any], chart2_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Service wrapper to calculate synastry aspects between two natal charts.

    Args:
        chart1_data (Dict[str, Any]): The first natal chart data.
        chart2_data (Dict[str, Any]): The second natal chart data.

    Returns:
        Dict[str, Any]: Synastry aspects data or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        engine = AstrologyEngine(ephemeris_path="ephemeris_data") # Zodiac/Ayanamsa don't matter for aspect difference
        synastry_aspects = engine.calculate_synastry_aspects(chart1_data, chart2_data)
        return {"synastry_aspects": synastry_aspects}
    except Exception as e:
        _logger.error(f"Error in get_synastry_aspects_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during synastry aspects calculation: {str(e)}"}

def get_composite_chart_service(chart1_data: Dict[str, Any], chart2_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Service wrapper to calculate a composite chart from two natal charts.

    Args:
        chart1_data (Dict[str, Any]): The first natal chart data.
        chart2_data (Dict[str, Any]): The second natal chart data.

    Returns:
        Dict[str, Any]: Composite chart data or an error message.
    """
    _logger = logging.getLogger(__name__)
    try:
        engine = AstrologyEngine(ephemeris_path="ephemeris_data")
        composite_chart = engine.calculate_composite_chart(chart1_data, chart2_data)
        return composite_chart
    except Exception as e:
        _logger.error(f"Error in get_composite_chart_service: {e}", exc_info=True)
        return {"error": f"An unexpected service error occurred during composite chart calculation: {str(e)}"}


# --- Export all public functions and classes for direct use ---
# This ensures that nothing is hidden and all exposed functionality is directly available.
__all__ = [
    'AstrologyEngine',
    'EphemerisManager',
    'HouseCalculator',
    'AspectCalculator',
    'PLANET_ID_MAP',
    'DEFAULT_NATAL_POINTS_NAMES',
    'ZODIAC_SIGNS',
    'SIGN_TO_ELEMENT',
    'SIGN_TO_MODALITY',
    'ASPECT_DEFINITIONS',
    'LUMINARIES',
    'PLANETS_FOR_ESSENTIAL_DIGNITIES',
    'ESSENTIAL_DIGNITY_RULES', # Exposed for full transparency if needed
    'POINT_DISPLAY_SYMBOLS', # Exposed for full transparency if needed
    'FIXED_STAR_J2000_DATA', # Exposed for full transparency if needed
    'HOUSE_SYSTEM_CHAR_CODES', # Exposed for full transparency if needed
    'ARABIC_PARTS_FORMULAS', # Exposed for full transparency if needed
    
    # Service functions (wrappers to use AstrologyEngine)
    'get_natal_chart_details_service',
    'get_daily_horoscope_data_service',
    'get_moon_phase_service',
    'get_transits_service',
    'get_progressions_service',
    'get_harmonic_chart_service',
    'get_midpoints_service',
    'get_antiscia_service',
    'get_arabic_parts_service',
    'get_solar_return_chart_service',
    'get_lunar_return_chart_service',
    'get_synastry_aspects_service',
    'get_composite_chart_service',
]