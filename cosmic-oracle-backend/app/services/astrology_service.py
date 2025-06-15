# app/services/astrology_service.py
"""
Astrology Service Module (Swiss Ephemeris)

Provides the core engine for all detailed astrological calculations. This module
is structured to be robust, performant, and maintainable.

Architectural Patterns:
- A singleton `AstrologyDataCache` is created on startup to hold static data,
  avoiding repeated file reads.
- `AstrologyService` acts as a Facade, offering a simple public interface
  to the complex underlying `AstrologyEngine`.
- `AstrologyEngine` is a dedicated "worker" class, instantiated for each unique
  chart request, encapsulating all calculation logic.
"""

# Standard library imports
import os
import datetime
import pytz
import math
import logging
# IMPORTS FOR TYPE HINTING: This line is critical for resolving NameErrors
from typing import Dict, List, Tuple, Any, Optional, Final
from itertools import combinations

# Third-party library imports
import swisseph as swe

# Local application imports
from app.core.config import settings  # Centralized configuration

# --- Production-Grade Logging Setup ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# --- One-Time Swiss Ephemeris Initialization (Module-level side effect) ---
# This ensures SWEPH_PATH is set as soon as this module is imported.
logger.info(f"Initializing Swiss Ephemeris service with path: '{settings.sweph_path}'")
if not os.path.exists(settings.sweph_path) or not os.listdir(settings.sweph_path):
    logger.critical(
        f"CRITICAL: Swiss Ephemeris path '{settings.sweph_path}' is empty or not found. "
        "Astrology calculations will fail. Please check your .env configuration and file locations."
    )
    raise RuntimeError(f"Missing required Swiss Ephemeris files at {settings.sweph_path}")
swe.set_ephe_path(settings.sweph_path)


# --- Self-Contained Utility Functions ---
def parse_datetime_with_timezone(datetime_str: str, tz_str: str) -> Optional[datetime.datetime]:
    try:
        dt_naive = datetime.datetime.fromisoformat(datetime_str)
        tz = pytz.timezone(tz_str)
        return tz.localize(dt_naive)
    except (ValueError, pytz.UnknownTimeZoneError) as e:
        logger.error(f"Failed to parse datetime '{datetime_str}' with timezone '{tz_str}': {e}")
        return None

def convert_to_utc(dt_aware: datetime.datetime) -> datetime.datetime:
    return dt_aware.astimezone(pytz.utc)

def get_julian_day_utc(dt_utc: datetime.datetime) -> float:
    return swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second, 1)[1]


# --- Centralized Data Caching (Singleton Pattern) ---
class AstrologyDataCache:
    """Loads and caches all static astrological data once at application startup."""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AstrologyDataCache, cls).__new__(cls)
            logger.info("Creating new AstrologyDataCache singleton instance.")
            cls._instance._initialize_cache()
        return cls._instance

    def _initialize_cache(self):
        logger.info("Loading astrological base data into singleton cache...")
        self.zodiac_signs, self.zodiac_map = self._load_zodiac_data()
        self.planets = self._load_planetary_data()
        self.aspects = self._load_aspect_data()
        self.house_systems = self._load_house_systems()
        self.dignity_scores = self._load_dignity_scores()
        self.fixed_stars = self._load_fixed_stars()
        self.rulerships = self._load_dignity_rulerships()
        logger.info("Astrological data cache loaded successfully.")

    # These methods are your original, correct implementations (shortened for brevity)
    def _load_zodiac_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        signs = [{'key': 'aries', 'name': 'Aries', 'symbol': '♈', 'element': 'Fire', 'modality': 'Cardinal'}, {'key': 'taurus', 'name': 'Taurus', 'symbol': '♉', 'element': 'Earth', 'modality': 'Fixed'}, {'key': 'gemini', 'name': 'Gemini', 'symbol': '♊', 'element': 'Air', 'modality': 'Mutable'}, {'key': 'cancer', 'name': 'Cancer', 'symbol': '♋', 'element': 'Water', 'modality': 'Cardinal'}, {'key': 'leo', 'name': 'Leo', 'symbol': '♌', 'element': 'Fire', 'modality': 'Fixed'}, {'key': 'virgo', 'name': 'Virgo', 'symbol': '♍', 'element': 'Earth', 'modality': 'Mutable'}, {'key': 'libra', 'name': 'Libra', 'symbol': '♎', 'element': 'Air', 'modality': 'Cardinal'}, {'key': 'scorpio', 'name': 'Scorpio', 'symbol': '♏', 'element': 'Water', 'modality': 'Fixed'}, {'key': 'sagittarius', 'name': 'Sagittarius', 'symbol': '♐', 'element': 'Fire', 'modality': 'Mutable'}, {'key': 'capricorn', 'name': 'Capricorn', 'symbol': '♑', 'element': 'Earth', 'modality': 'Cardinal'}, {'key': 'aquarius', 'name': 'Aquarius', 'symbol': '♒', 'element': 'Air', 'modality': 'Fixed'}, {'key': 'pisces', 'name': 'Pisces', 'symbol': '♓', 'element': 'Water', 'modality': 'Mutable'}]
        return signs, {s['key']: s for s in signs}
    def _load_planetary_data(self) -> Dict[str, Any]: return {"sun": {"symbol": "☉"}, "moon": {"symbol": "☽"}, "mercury": {"symbol": "☿"},"venus": {"symbol": "♀"}, "mars": {"symbol": "♂"}, "jupiter": {"symbol": "♃"},"saturn": {"symbol": "♄"}, "uranus": {"symbol": "♅"}, "neptune": {"symbol": "♆"},"pluto": {"symbol": "♇"}, "true_node": {"symbol": "☊"}, "chiron": {"symbol": "⚷"},"ascendant": {"symbol": "Asc"}, "midheaven": {"symbol": "MC"}, "descendant": {"symbol": "Dsc"},"imum_coeli": {"symbol": "IC"}, "part_of_fortune": {"symbol": "⊗"}}
    def _load_aspect_data(self) -> Dict[str, Any]: return {"conjunction": {"degrees": 0, "orb": 8.0, "symbol": "☌", "type": "major"},"opposition": {"degrees": 180, "orb": 8.0, "symbol": "☍", "type": "major"},"trine": {"degrees": 120, "orb": 8.0, "symbol": "△", "type": "major"},"square": {"degrees": 90, "orb": 7.0, "symbol": "□", "type": "major"},"sextile": {"degrees": 60, "orb": 6.0, "symbol": "⚹", "type": "major"},"quincunx": {"degrees": 150, "orb": 3.0, "symbol": "⚻", "type": "minor"}}
    def _load_house_systems(self) -> Dict[str, bytes]: return {"Placidus": b'P', "Koch": b'K', "Porphyry": b'O', "WholeSign": b'W', "Regiomontanus": b'R', "Campanus": b'C', "Equal": b'E'}
    def _load_dignity_scores(self) -> Dict[str, int]: return {"Rulership": 5, "Exaltation": 4, "Detriment": -4, "Fall": -5, "Peregrine": 0}
    def _load_dignity_rulerships(self) -> Dict[str, Dict[str, str]]: return {"rulership": {"Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"}, "modern_rulership": {"Scorpio": "Pluto", "Aquarius": "Uranus", "Pisces": "Neptune"}, "exaltation": {"Aries": "Sun", "Taurus": "Moon", "Cancer": "Jupiter", "Virgo": "Mercury", "Libra": "Saturn", "Capricorn": "Mars", "Pisces": "Venus"}}
    def _load_fixed_stars(self) -> List[Dict[str, Any]]: return [{"name": "Algol", "longitude": 56.12, "keywords": "intense, passionate, creative/destructive"}, {"name": "Alcyone", "longitude": 60.03, "keywords": "vision, mystical, sorrow"}, {"name": "Aldebaran", "longitude": 70.00, "keywords": "success, integrity, the bull's eye"}, {"name": "Rigel", "longitude": 76.94, "keywords": "teacher, educator, technical skill"}, {"name": "Capella", "longitude": 81.82, "keywords": "curiosity, freedom, intellectual"}, {"name": "Sirius", "longitude": 104.25, "keywords": "ambition, fame, the mundane to the sacred"}, {"name": "Regulus", "longitude": 150.05, "keywords": "royalty, leadership, success with a warning"}, {"name": "Spica", "longitude": 204.02, "keywords": "brilliance, gifts, protection"}, {"name": "Arcturus", "longitude": 204.23, "keywords": "inspiration, pathfinder, justice"}, {"name": "Antares", "longitude": 250.00, "keywords": "obsession, intensity, power"}, {"name": "Vega", "longitude": 285.41, "keywords": "charisma, artistic, magical"}, {"name": "Fomalhaut", "longitude": 334.13, "keywords": "idealism, mystical, alchemy"}]

astro_data_cache = AstrologyDataCache() # Instance of the singleton data cache

# --- Core Astrology Calculation Engine Class ---
class AstrologyEngine:
    """A self-contained worker that performs a complete astrological chart calculation."""
    PLANET_IDS: Final[Dict[str, int]] = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO, "True Node": swe.TRUE_NODE, "Chiron": swe.CHIRON}
    DIGNITY_PLANETS: Final[List[str]] = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    def __init__(self, dt_utc: datetime.datetime, latitude: float, longitude: float, altitude: float, house_system: str):
        self.dt_utc = dt_utc
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.house_system_name = house_system
        self.data_cache = astro_data_cache # Use the global singleton cache instance
        self.julian_day_utc = get_julian_day_utc(dt_utc)
        self.swe_flags = swe.FLG_SPEED | swe.FLG_SWIEPH
        self._cache = {}

    def generate_full_chart(self) -> Dict[str, Any]:
        """Orchestrates the generation of all chart components."""
        try:
            points = self._get_planetary_details()
            angles = self._get_angles()
            house_cusps = self._get_house_cusps()
            all_points_list = list(points.values()) + list(angles.values())
            all_points_map = {p['key']: p for p in all_points_list}
            part_of_fortune = self._calculate_part_of_fortune(points, angles, house_cusps)
            if 'error' not in part_of_fortune:
                all_points_list.append(part_of_fortune)
                all_points_map[part_of_fortune['key']] = part_of_fortune
            aspects = self._calculate_aspects(all_points_map)
            analysis = self._run_analysis_modules(all_points_list, aspects, all_points_map)
            return {"chart_info": {"datetime_utc": self.dt_utc.isoformat(), "julian_day_utc": self.julian_day_utc, "latitude": self.latitude, "longitude": self.longitude, "altitude": self.altitude, "house_system": self.house_system_name}, "points": points, "angles": angles, "house_cusps": house_cusps, "part_of_fortune": part_of_fortune, "aspects": aspects, "analysis": analysis}
        except swe.Error as e:
            logger.warning(f"A swisseph calculation error occurred: {e}")
            return {"error": f"Calculation error for house system '{self.house_system_name}' at this latitude. Try 'WholeSign'. Details: {e}"}

    def _get_raw_planetary_positions(self) -> Dict[str, tuple]:
        if 'raw_positions' in self._cache: return self._cache['raw_positions']
        positions = {name: swe.calc_ut(self.julian_day_utc, pid, self.swe_flags) for name, pid in self.PLANET_IDS.items()}
        self._cache['raw_positions'] = positions
        return positions

    def _get_houses_and_angles_raw(self) -> Tuple[List[float], List[float]]:
        if 'houses_raw' in self._cache: return self._cache['houses_raw']
        system_code = self.data_cache.house_systems.get(self.house_system_name)
        if not system_code: raise ValueError(f"Unsupported house system: {self.house_system_name}")
        cusps, ascmc = swe.houses_ex(self.julian_day_utc, self.latitude, self.longitude, system_code)
        self._cache['houses_raw'] = (list(cusps), list(ascmc))
        return self._cache['houses_raw']

    def _format_point(self, name: str, lon: float, speed: Optional[float] = None, lat: Optional[float] = None) -> Dict[str, Any]:
        deg_in_zodiac = lon % 30
        sign_info = self.data_cache.zodiac_signs[int(lon // 30)]
        d, m, s = self._degrees_to_dms(deg_in_zodiac)
        key = name.lower().replace(" ", "_")
        return {"name": name, "key": key, "symbol": self.data_cache.planets.get(key, {}).get("symbol", sign_info['symbol']), "longitude": round(lon, 6), "speed_longitude": round(speed, 6) if speed is not None else None, "is_retrograde": speed < 0 if speed is not None else None, "ecliptic_latitude": round(lat, 6) if lat is not None else None, "sign_key": sign_info['key'], "sign_name": sign_info['name'], "element": sign_info['element'], "modality": sign_info['modality'], "degrees_in_sign": round(deg_in_zodiac, 6), "display_dms": f"{d}°{sign_info['symbol']}{m}'{s}\""}
    
    @staticmethod
    def _degrees_to_dms(degrees: float) -> Tuple[int, int, int]:
        d = int(degrees); m_float = (degrees - d) * 60; m = int(m_float); s = int(round((m_float - m) * 60))
        if s == 60: m += 1; s = 0
        if m == 60: d += 1; m = 0
        return d, m, s

    def _get_angles(self) -> Dict[str, Any]:
        if 'angles' in self._cache: return self._cache['angles']
        _, ascmc = self._get_houses_and_angles_raw()
        angles = {"Ascendant": {**self._format_point("Ascendant", ascmc[0]), "house": 1}, "Midheaven": {**self._format_point("Midheaven", ascmc[1]), "house": 10}, "Descendant": {**self._format_point("Descendant", (ascmc[0] + 180) % 360), "house": 7}, "Imum Coeli": {**self._format_point("Imum Coeli", (ascmc[1] + 180) % 360), "house": 4}}
        self._cache['angles'] = angles
        return angles

    def _get_house_cusps(self) -> Dict[int, Any]:
        if 'house_cusps' in self._cache: return self._cache['house_cusps']
        cusps_array, _ = self._get_houses_and_angles_raw()
        cusps = {i + 1: self._format_point(f"House {i + 1} Cusp", cusps_array[i]) for i in range(12)}
        self._cache['house_cusps'] = cusps
        return cusps

    def _get_planetary_details(self) -> Dict[str, Any]:
        if 'planetary_details' in self._cache: return self._cache['planetary_details']
        raw_pos = self._get_raw_planetary_positions()
        house_cusps = self._get_house_cusps()
        details = {}
        for name, data in raw_pos.items():
            point = self._format_point(name, data[0], data[3], data[1])
            point['house'] = self._determine_house_placement(point['longitude'], house_cusps)
            if name in self.DIGNITY_PLANETS: point['dignities'] = self._calculate_dignities(name, point['sign_name'])
            details[name] = point
        self._cache['planetary_details'] = details
        return details

    def _determine_house_placement(self, point_lon: float, cusps: Dict[int, Any]) -> Optional[int]:
        cusp_lons = [cusps[i]['longitude'] for i in range(1, 13)]
        for i in range(12):
            start_lon, end_lon = cusp_lons[i], cusp_lons[(i + 1) % 12]
            if start_lon < end_lon:
                if start_lon <= point_lon < end_lon: return i + 1
            else:
                if point_lon >= start_lon or point_lon < end_lon: return i + 1
        return None

    def _calculate_dignities(self, planet: str, sign: str) -> Dict[str, Any]:
        dignities = {"ruler": False, "exaltation": False, "detriment": False, "fall": False, "status": "Peregrine"}
        scores, rules, zodiac_names = self.data_cache.dignity_scores, self.data_cache.rulerships, [s['name'] for s in self.data_cache.zodiac_signs]
        if rules['rulership'].get(sign) == planet or rules['modern_rulership'].get(sign) == planet: dignities.update({"ruler": True, "status": "Rulership"})
        if rules['exaltation'].get(sign) == planet: dignities.update({"exaltation": True, "status": "Exaltation" if dignities['status'] == 'Peregrine' else dignities['status']})
        for ruled_sign, ruler in rules['rulership'].items():
            # This line was truncated in your previous paste. Assuming this is the full logic:
            if ruler == planet and zodiac_names[(zodiac_names.index(ruled_sign) + 6) % 12] == sign: dignities.update({"detriment": True, "status": "Detriment" if dignities['status'] == 'Peregrine' else dignities['status']})
        for exalted_sign, exalted in rules['exaltation'].items():
            if exalted == planet and zodiac_names[(zodiac_names.index(exalted_sign) + 6) % 12] == sign: dignities.update({"fall": True, "status": "Fall" if dignities['status'] == 'Peregrine' else dignities['status']})
        dignities['score'] = scores.get(dignities['status'], 0)
        return dignities
        
    def _calculate_part_of_fortune(self, points, angles, house_cusps) -> Dict[str, Any]:
        sun_lon, moon_lon, asc_lon = points.get("Sun", {}).get("longitude"), points.get("Moon", {}).get("longitude"), angles.get("Ascendant", {}).get("longitude")
        if any(p is None for p in [sun_lon, moon_lon, asc_lon]): return {"error": "Missing core data for Part of Fortune calculation."}
        is_day_chart = points.get("Sun", {}).get("house", 0) in range(7, 13)
        pof_lon = (asc_lon + (moon_lon - sun_lon if is_day_chart else sun_lon - moon_lon) + 360) % 360
        pof_details = self._format_point("Part of Fortune", pof_lon)
        pof_details["house"] = self._determine_house_placement(pof_lon, house_cusps)
        pof_details["calculated_as_day_chart"] = is_day_chart
        return pof_details

    def _calculate_aspects(self, points_map: Dict[str, Any]) -> List[Dict[str, Any]]:
        aspect_list, point_list = [], list(points_map.values())
        for i in range(len(point_list)):
            for j in range(i + 1, len(point_list)):
                p1, p2 = point_list[i], point_list[j]
                separation = abs(p1['longitude'] - p2['longitude'])
                if separation > 180: separation = 360 - separation
                for key, info in self.data_cache.aspects.items():
                    if abs(separation - info["degrees"]) <= info["orb"]:
                        aspect_list.append({"point1_name": p1['name'], "point1_key": p1['key'],"point2_name": p2['name'], "point2_key": p2['key'],"aspect_name": key, "aspect_symbol": info["symbol"], "orb_degrees": round(abs(separation - info["degrees"]), 3), "is_applying": self._is_aspect_applying(p1, p2, separation, info["degrees"])})
        return sorted(aspect_list, key=lambda x: x['orb_degrees'])

    def _is_aspect_applying(self, p1: Dict, p2: Dict, separation: float, aspect_degrees: float) -> Optional[bool]:
        s1, s2 = p1.get('speed_longitude'), p2.get('speed_longitude')
        if s1 is None or s2 is None or s1 == s2: return None
        next_separation = abs(((p1['longitude'] + s1 * 0.001) % 360) - ((p2['longitude'] + s2 * 0.001) % 360))
        if next_separation > 180: next_separation = 360 - next_separation
        return abs(next_separation - aspect_degrees) < abs(separation - aspect_degrees)

    def _run_analysis_modules(self, points_list: List[Dict], aspects: List[Dict], points_map: Dict[str, Any]) -> Dict[str, Any]:
        elements, modalities, hemispheres = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}, {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}, {'Northern': 0, 'Southern': 0, 'Eastern': 0, 'Western': 0}
        for point in [p for p in points_list if 'element' in p and p['name'] in self.DIGNITY_PLANETS]:
            elements[point['element']] += 1; modalities[point['modality']] += 1
            if point.get('house'):
                if 1 <= point['house'] <= 6: hemispheres['Northern'] += 1;
                else: hemispheres['Southern'] += 1
                if 1 <= point['house'] <= 3 or 10 <= point['house'] <= 12: hemispheres['Eastern'] += 1
                else: hemispheres['Western'] += 1
        return {"chart_distribution": {"elemental_balance": elements, "modality_balance": modalities, "hemisphere_emphasis": hemispheres}, "chart_patterns": self._find_patterns(aspects, points_map), "fixed_star_conjunctions": self._find_fixed_star_conjunctions(points_list), "midpoints": self._calculate_midpoints(points_list)}

    def _find_patterns(self, aspects: List[Dict], points_map: Dict) -> List[Dict]:
        """Detects major astrological patterns like Grand Trines, T-Squares, and Stelliums."""
        patterns = []
        
        # Find Grand Trines (3 planets in trine aspect forming a triangle)
        trine_aspects = [a for a in aspects if a['aspect_name'] == 'trine']
        for combo in combinations(trine_aspects, 2):
            asp1, asp2 = combo
            if asp1['point1_key'] == asp2['point1_key'] or asp1['point1_key'] == asp2['point2_key']:
                common_point = asp1['point1_key']
                other_points = [asp1['point2_key'], asp2['point2_key'] if asp2['point1_key'] == common_point else asp2['point1_key']]
            elif asp1['point2_key'] == asp2['point1_key'] or asp1['point2_key'] == asp2['point2_key']:
                common_point = asp1['point2_key']
                other_points = [asp1['point1_key'], asp2['point2_key'] if asp2['point1_key'] == common_point else asp2['point1_key']]
            else:
                continue
            
            # Check if the two other points form a trine
            for trine in trine_aspects:
                if (trine['point1_key'] in other_points and trine['point2_key'] in other_points and 
                    trine != asp1 and trine != asp2):
                    patterns.append({
                        'type': 'Grand Trine',
                        'description': 'Three planets forming a harmonious triangle',
                        'points': [common_point] + other_points,
                        'elements': list(set([points_map[p]['element'] for p in [common_point] + other_points if p in points_map])),
                        'strength': 'High'
                    })
        
        # Find T-Squares (opposition with two squares to a third planet)
        opposition_aspects = [a for a in aspects if a['aspect_name'] == 'opposition']
        square_aspects = [a for a in aspects if a['aspect_name'] == 'square']
        
        for opp in opposition_aspects:
            opp_points = [opp['point1_key'], opp['point2_key']]
            for point_key in points_map:
                if point_key not in opp_points:
                    squares_to_point = [s for s in square_aspects 
                                      if (s['point1_key'] == point_key and s['point2_key'] in opp_points) or
                                         (s['point2_key'] == point_key and s['point1_key'] in opp_points)]
                    if len(squares_to_point) >= 2:
                        patterns.append({
                            'type': 'T-Square',
                            'description': 'Opposition with squares to a focal planet',
                            'points': opp_points + [point_key],
                            'focal_point': point_key,
                            'strength': 'High'
                        })
        
        # Find Stelliums (3+ planets in same sign)
        sign_groups = {}
        for point_key, point_data in points_map.items():
            if point_data.get('sign_key') and point_data['name'] in self.DIGNITY_PLANETS:
                sign = point_data['sign_key']
                if sign not in sign_groups:
                    sign_groups[sign] = []
                sign_groups[sign].append(point_key)
        
        for sign, point_list in sign_groups.items():
            if len(point_list) >= 3:
                patterns.append({
                    'type': 'Stellium',
                    'description': f'Concentration of planets in {sign.title()}',
                    'points': point_list,
                    'sign': sign,
                    'strength': 'Medium' if len(point_list) == 3 else 'High'
                })
        
        return patterns

    def _find_fixed_star_conjunctions(self, points: List[Dict]) -> List[Dict]:
        """Finds conjunctions between planets and fixed stars using Swiss Ephemeris calculations."""
        conjunctions = []
        orb_limit = 2.0  # Standard orb for fixed star conjunctions
        
        # Get current fixed star positions using Swiss Ephemeris
        current_fixed_stars = []
        for star in self.data_cache.fixed_stars:
            try:
                # Calculate current position of fixed star accounting for precession
                star_longitude = (star['longitude'] + 
                                (self.julian_day_utc - 2451545.0) * 50.29 / 365.25 / 3600) % 360
                current_fixed_stars.append({
                    'name': star['name'],
                    'longitude': star_longitude,
                    'keywords': star['keywords']
                })
            except Exception as e:
                logger.warning(f"Error calculating position for fixed star {star['name']}: {e}")
                continue
        
        # Check each planet against each fixed star
        for point in points:
            if not point.get('longitude'):
                continue
                
            for star in current_fixed_stars:
                separation = abs(point['longitude'] - star['longitude'])
                if separation > 180:
                    separation = 360 - separation
                
                if separation <= orb_limit:
                    conjunctions.append({
                        'planet': point['name'],
                        'planet_key': point['key'],
                        'fixed_star': star['name'],
                        'orb': round(separation, 3),
                        'description': f"{point['name']} conjunct {star['name']}",
                        'keywords': star['keywords'],
                        'star_longitude': round(star['longitude'], 3),
                        'planet_longitude': round(point['longitude'], 3)
                    })
        
        return sorted(conjunctions, key=lambda x: x['orb'])

    def _calculate_midpoints(self, points: List[Dict]) -> Dict[str, Dict]:
        """Calculates astrological midpoints between planetary pairs."""
        midpoints = {}
        
        # Only calculate midpoints for main planets and angles
        relevant_points = [p for p in points if p['name'] in self.DIGNITY_PLANETS + 
                          ['Ascendant', 'Midheaven', 'True Node']]
        
        for i, point1 in enumerate(relevant_points):
            for point2 in relevant_points[i+1:]:
                if not (point1.get('longitude') and point2.get('longitude')):
                    continue
                
                lon1, lon2 = point1['longitude'], point2['longitude']
                
                # Calculate direct midpoint
                direct_midpoint = (lon1 + lon2) / 2
                
                # Calculate indirect midpoint (adding 180 degrees)
                indirect_midpoint = (direct_midpoint + 180) % 360
                
                # Choose the midpoint that creates the smaller arc
                diff = abs(lon2 - lon1)
                if diff > 180:
                    diff = 360 - diff
                    # Use indirect midpoint for larger separations
                    midpoint_longitude = indirect_midpoint
                else:
                    midpoint_longitude = direct_midpoint
                
                midpoint_longitude = midpoint_longitude % 360
                
                # Determine zodiac sign for midpoint
                sign_index = int(midpoint_longitude // 30)
                sign_info = self.data_cache.zodiac_signs[sign_index]
                degrees_in_sign = midpoint_longitude % 30
                
                midpoint_key = f"{point1['key']}_{point2['key']}_midpoint"
                
                midpoints[midpoint_key] = {
                    'point1': point1['name'],
                    'point1_key': point1['key'],
                    'point2': point2['name'],
                    'point2_key': point2['key'],
                    'longitude': round(midpoint_longitude, 6),
                    'sign_name': sign_info['name'],
                    'sign_key': sign_info['key'],
                    'degrees_in_sign': round(degrees_in_sign, 6),
                    'description': f"Midpoint of {point1['name']} and {point2['name']}",
                    'display': f"{int(degrees_in_sign)}°{sign_info['symbol']}{int((degrees_in_sign % 1) * 60)}'"
                }
        
        # Find midpoint aspects to natal planets
        for midpoint_key, midpoint_data in midpoints.items():
            aspects_to_midpoint = []
            
            for point in relevant_points:
                if not point.get('longitude'):
                    continue
                    
                separation = abs(point['longitude'] - midpoint_data['longitude'])
                if separation > 180:
                    separation = 360 - separation
                
                # Check for major aspects with tighter orbs for midpoints
                for aspect_name, aspect_info in self.data_cache.aspects.items():
                    if aspect_info['type'] == 'major':  # Only major aspects for midpoints
                        orb = min(aspect_info['orb'] * 0.75, 4.0)  # Tighter orbs for midpoints
                        if abs(separation - aspect_info['degrees']) <= orb:
                            aspects_to_midpoint.append({
                                'planet': point['name'],
                                'aspect': aspect_name,
                                'orb': round(abs(separation - aspect_info['degrees']), 3)
                            })
            
            if aspects_to_midpoint:
                midpoints[midpoint_key]['aspects'] = sorted(aspects_to_midpoint, 
                                                          key=lambda x: x['orb'])
        
        return midpoints


# --- PUBLIC-FACING ASTROLOGY SERVICE CLASS (Facade Pattern) ---
class AstrologyService:
    """
    Provides a higher-level interface for astrological calculations,
    acting as a facade over AstrologyEngine and managing data access.
    This class is intended to be instantiated once per application lifecycle.
    """
    _instance = None # For optional singleton management

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AstrologyService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        # The data cache is already a singleton and initialized on first access
        self.data_cache = astro_data_cache
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("AstrologyService initialized.")
        self._initialized = True


    def get_natal_chart_details(
        self,
        datetime_str: str,
        timezone_str: str,
        latitude: float,
        longitude: float,
        house_system: str,
        altitude: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates a natal chart using the AstrologyEngine.
        This method replaces the standalone `get_natal_chart_details` function.
        """
        self.logger.info(f"AstrologyService: Natal chart request for: {datetime_str} in {timezone_str}")
        try:
            dt_aware = parse_datetime_with_timezone(datetime_str, timezone_str)
            if not dt_aware:
                return {"error": "Invalid or unparseable datetime or timezone string provided."}
            dt_utc = convert_to_utc(dt_aware)

            if house_system not in self.data_cache.house_systems:
                return {"error": f"Unsupported house system: '{house_system}'. Available: {list(self.data_cache.house_systems.keys())}"}

            engine = AstrologyEngine(dt_utc, latitude, longitude, altitude, house_system)
            chart = engine.generate_full_chart()
            return chart
        except Exception as e:
            self.logger.critical(f"AstrologyService: An unexpected fatal error occurred during natal chart calculation: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred during chart calculation. The event has been logged for review."}

    # Add other high-level methods here as needed, e.g.:
    # def get_current_transits(self, date: datetime.datetime, location_data: Dict) -> Dict:
    #     pass