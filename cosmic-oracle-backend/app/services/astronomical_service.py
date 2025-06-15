"""
Astronomical calculations service using PySwissEph and Skyfield for precise calculations.
"""
import swisseph as swe
from skyfield.api import load, utc
from skyfield.units import Angle
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple, Optional

# Initialize Swiss Ephemeris with path to ephemeris files
EPHEMERIS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
swe.set_ephe_path(EPHEMERIS_PATH)

# Load Skyfield data
ts = load.timescale()
planets = load('de421.bsp')

class AstronomicalService:
    """Service for precise astronomical and astrological calculations."""
    
    PLANETS = {
        'sun': swe.SUN,
        'moon': swe.MOON,
        'mercury': swe.MERCURY,
        'venus': swe.VENUS,
        'mars': swe.MARS,
        'jupiter': swe.JUPITER,
        'saturn': swe.SATURN,
        'uranus': swe.URANUS,
        'neptune': swe.NEPTUNE,
        'pluto': swe.PLUTO
    }

    ZODIAC_SIGNS = [
        'Aries', 'Taurus', 'Gemini', 'Cancer',
        'Leo', 'Virgo', 'Libra', 'Scorpio',
        'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]

    def __init__(self):
        """Initialize the astronomical service."""
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set sidereal mode if needed

    def get_planet_position(self, planet: str, date_time: datetime) -> Dict:
        """Get precise planetary position for a given date and time."""
        julian_day = self._get_julian_day(date_time)
        planet_id = self.PLANETS.get(planet.lower())
        
        if planet_id is None:
            raise ValueError(f"Invalid planet: {planet}")

        flags = swe.FLG_SWIEPH + swe.FLG_SPEED
        position = swe.calc_ut(julian_day, planet_id, flags)

        longitude = position[0][0]  # Longitude in degrees
        latitude = position[0][1]   # Latitude in degrees
        distance = position[0][2]   # Distance in AU
        speed = position[0][3]      # Speed in longitude (deg/day)

        zodiac_sign = self.ZODIAC_SIGNS[int(longitude / 30)]
        degrees_in_sign = longitude % 30

        return {
            'planet': planet,
            'longitude': longitude,
            'latitude': latitude,
            'distance': distance,
            'speed': speed,
            'zodiac_sign': zodiac_sign,
            'degrees_in_sign': degrees_in_sign,
            'is_retrograde': speed < 0,
            'julian_day': julian_day
        }

    def calculate_moon_phase(self, date_time: datetime) -> Dict:
        """Calculate precise moon phase using Swiss Ephemeris."""
        julian_day = self._get_julian_day(date_time)
        phase = swe.pheno_ut(julian_day, swe.MOON, swe.FLG_SWIEPH)[1]
        illumination = (1 + phase) / 2 * 100  # Convert to percentage

        # Calculate days since last new moon
        last_new_moon = swe.nlun_ut(julian_day, swe.NLUN_PRECESS, -1)[1]
        days_since_new = julian_day - last_new_moon

        # Get precise phase name based on days since new moon
        phase_name = self._get_precise_phase_name(days_since_new)

        return {
            'phase_name': phase_name,
            'illumination': illumination,
            'days_since_new': days_since_new,
            'julian_day': julian_day
        }

    def calculate_birth_chart(self, date_time: datetime, latitude: float, longitude: float) -> Dict:
        """Calculate full birth chart with houses, aspects, and angles using Swiss Ephemeris."""
        julian_day = self._get_julian_day(date_time)
        
        # Calculate houses using Placidus system (default)
        houses = swe.houses_ex(julian_day, latitude, longitude, b'P')
        
        # Calculate all planetary positions
        planets_data = {}
        aspects = []
        for planet_name, planet_id in self.PLANETS.items():
            pos = self.get_planet_position(planet_name, date_time)
            planets_data[planet_name] = pos
            
            # Calculate aspects with previously calculated planets
            for other_planet, other_data in planets_data.items():
                if other_planet != planet_name:
                    aspect = self._calculate_aspect(
                        pos['longitude'],
                        other_data['longitude']
                    )
                    if aspect:
                        aspects.append({
                            'planet1': planet_name,
                            'planet2': other_planet,
                            'aspect_type': aspect['type'],
                            'orb': aspect['orb']
                        })

        # Calculate important angles (Ascendant, Midheaven, etc.)
        angles = {
            'ascendant': houses[1][0],
            'midheaven': houses[2][0],
            'descendant': (houses[1][0] + 180) % 360,
            'imum_coeli': (houses[2][0] + 180) % 360
        }

        # Format houses data
        houses_data = {}
        for i in range(12):
            houses_data[i + 1] = {
                'cusp': houses[0][i],
                'sign': self.ZODIAC_SIGNS[int(houses[0][i] / 30)],
                'degrees_in_sign': houses[0][i] % 30
            }

        return {
            'planets': planets_data,
            'houses': houses_data,
            'aspects': aspects,
            'angles': angles,
            'julian_day': julian_day,
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            }
        }

    def calculate_next_eclipse(self, date_time: datetime) -> Dict:
        """Calculate the next solar and lunar eclipses."""
        julian_day = self._get_julian_day(date_time)
        
        # Find next solar eclipse
        solar = swe.sol_eclipse_when_glob(julian_day)
        solar_date = self._julian_to_datetime(solar[1][0])
        
        # Find next lunar eclipse
        lunar = swe.lun_eclipse_when(julian_day)
        lunar_date = self._julian_to_datetime(lunar[1][0])

        return {
            'next_solar_eclipse': {
                'date': solar_date,
                'type': self._get_eclipse_type(solar[0]),
                'julian_day': solar[1][0]
            },
            'next_lunar_eclipse': {
                'date': lunar_date,
                'type': self._get_eclipse_type(lunar[0]),
                'julian_day': lunar[1][0]
            }
        }

    def calculate_lunar_nodes(self, date_time: datetime) -> Dict:
        """Calculate true and mean lunar nodes and apogee/perigee."""
        julian_day = self._get_julian_day(date_time)
        
        # Calculate true node
        true_node = swe.calc_ut(julian_day, swe.TRUE_NODE, swe.FLG_SWIEPH)
        
        # Calculate mean node
        mean_node = swe.calc_ut(julian_day, swe.MEAN_NODE, swe.FLG_SWIEPH)
        
        # Calculate lunar apogee (Black Moon Lilith)
        lilith = swe.calc_ut(julian_day, swe.MEAN_APOG, swe.FLG_SWIEPH)

        return {
            'true_node': {
                'longitude': true_node[0][0],
                'latitude': true_node[0][1],
                'speed': true_node[0][3],
                'sign': self.ZODIAC_SIGNS[int(true_node[0][0] / 30)]
            },
            'mean_node': {
                'longitude': mean_node[0][0],
                'latitude': mean_node[0][1],
                'speed': mean_node[0][3],
                'sign': self.ZODIAC_SIGNS[int(mean_node[0][0] / 30)]
            },
            'lilith': {
                'longitude': lilith[0][0],
                'latitude': lilith[0][1],
                'speed': lilith[0][3],
                'sign': self.ZODIAC_SIGNS[int(lilith[0][0] / 30)]
            }
        }

    def calculate_fixed_star_positions(self, date_time: datetime, stars: List[str]) -> Dict:
        """Calculate positions of fixed stars."""
        julian_day = self._get_julian_day(date_time)
        star_positions = {}
        
        for star_name in stars:
            try:
                # Get star info
                star = swe.fixstar2_ut(star_name, julian_day)
                
                star_positions[star_name] = {
                    'longitude': star[0][0],
                    'latitude': star[0][1],
                    'distance': star[0][2],
                    'sign': self.ZODIAC_SIGNS[int(star[0][0] / 30)],
                    'degrees_in_sign': star[0][0] % 30
                }
            except Exception as e:
                print(f"Error calculating position for star {star_name}: {str(e)}")
                continue
                
        return star_positions

    def get_ephemeris_data(self, body: str, start_date: datetime, end_date: datetime, interval_hours: int = 24) -> List[Dict]:
        """Get ephemeris data for a celestial body over a time period."""
        if body.lower() not in self.PLANETS:
            raise ValueError(f"Invalid body: {body}")

        data_points = []
        current_time = start_date
        
        while current_time <= end_date:
            position = self.get_planet_position(body, current_time)
            
            # Add heliacal rising/setting info if it's a planet
            if body.lower() not in ['sun', 'moon']:
                heliacal = self._calculate_heliacal_events(body, current_time, 0, 0)  # Using default observer position
                position.update(heliacal)
            
            data_points.append({
                'timestamp': current_time.isoformat(),
                **position
            })
            
            current_time = current_time + timedelta(hours=interval_hours)
            
        return data_points

    def _calculate_heliacal_events(self, body: str, date_time: datetime, latitude: float, longitude: float) -> Dict:
        """Calculate heliacal rising, setting, and visibility conditions."""
        jd = self._get_julian_day(date_time)
        body_id = self.PLANETS[body.lower()]
        
        # Get atmospheric conditions (using default values)
        atmospheric_params = (
            1013.25,  # Pressure in mbar
            15,       # Temperature in Celsius
            50,       # Relative humidity %
            0.25      # Atmospheric dust
        )
        
        try:
            result = swe.heliacal_ut(
                jd,                    # Julian day
                longitude, latitude,   # Observer position
                atmospheric_params,    # Atmospheric conditions
                0,                    # Observer altitude
                10,                   # Observer age (affects visibility calculation)
                body_id,              # Celestial body
                swe.FLG_SWIEPH       # Ephemeris flag
            )
            
            return {
                'heliacal_rising': self._julian_to_datetime(result[0]),
                'heliacal_setting': self._julian_to_datetime(result[1]),
                'evening_visibility': result[2],
                'morning_visibility': result[3]
            }
        except Exception:
            return {}  # Return empty dict if calculation fails

    def _get_julian_day(self, date_time: datetime) -> float:
        """Convert datetime to Julian Day."""
        return swe.julday(
            date_time.year,
            date_time.month,
            date_time.day,
            date_time.hour + date_time.minute/60.0 + date_time.second/3600.0
        )

    def _julian_to_datetime(self, julian_day: float) -> datetime:
        """Convert Julian Day to datetime."""
        dt = swe.revjul(julian_day)
        return datetime(
            dt[0], dt[1], dt[2],
            int(dt[3]),
            int((dt[3] % 1) * 60),
            int(((dt[3] % 1) * 60 % 1) * 60)
        )

    def _get_precise_phase_name(self, days_since_new: float) -> str:
        """Get precise moon phase name based on days since new moon."""
        phase_length = 29.53058770576  # Synodic month (new moon to new moon)
        phase_angle = (days_since_new / phase_length) * 360
        
        # More precise phase names
        if 0 <= phase_angle < 45:
            return "New Moon - Waxing Crescent"
        elif 45 <= phase_angle < 90:
            return "Waxing Crescent - First Quarter"
        elif 90 <= phase_angle < 135:
            return "First Quarter - Waxing Gibbous"
        elif 135 <= phase_angle < 180:
            return "Waxing Gibbous - Full Moon"
        elif 180 <= phase_angle < 225:
            return "Full Moon - Waning Gibbous"
        elif 225 <= phase_angle < 270:
            return "Waning Gibbous - Last Quarter"
        elif 270 <= phase_angle < 315:
            return "Last Quarter - Waning Crescent"
        else:
            return "Waning Crescent - New Moon"

    def _calculate_aspect(self, lon1: float, lon2: float) -> Optional[Dict]:
        """Calculate the aspect between two planetary positions."""
        # Major aspects and their orbs
        ASPECTS = {
            0: {'type': 'conjunction', 'orb': 10},
            60: {'type': 'sextile', 'orb': 6},
            90: {'type': 'square', 'orb': 8},
            120: {'type': 'trine', 'orb': 8},
            180: {'type': 'opposition', 'orb': 10}
        }

        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff

        for angle, aspect_data in ASPECTS.items():
            orb = aspect_data['orb']
            if abs(diff - angle) <= orb:
                return {
                    'type': aspect_data['type'],
                    'orb': abs(diff - angle)
                }
        return None

    def _get_eclipse_type(self, eclipse_type: int) -> str:
        """Convert Swiss Ephemeris eclipse type to human-readable string."""
        types = {
            swe.ECL_TOTAL: 'Total',
            swe.ECL_ANNULAR: 'Annular',
            swe.ECL_PARTIAL: 'Partial',
            swe.ECL_VISIBLE: 'Visible',
            swe.ECL_MAX_VISIBLE: 'Maximum Visible',
            swe.ECL_CENTRAL: 'Central'
        }
        eclipse_types = []
        for key, value in types.items():
            if eclipse_type & key:
                eclipse_types.append(value)
        return ', '.join(eclipse_types) if eclipse_types else 'Unknown'
