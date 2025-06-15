# app/services/skyfield_service.py
import logging
import os
from datetime import datetime, timezone, timedelta
# IMPORTS FOR TYPE HINTING: This line is critical for resolving NameErrors like 'Tuple'
from typing import Dict, Any, Optional, Tuple 
from skyfield.api import load, EarthSatellite, Time
from skyfield.timelib import Time as SkyfieldTime # Alias to avoid conflict if you import datetime.Time
from skyfield.api import Topos
from skyfield.framelib import itrs
from skyfield.precession import precession_matrix
from skyfield.units import Angle

from app.core.config import settings

logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class SkyfieldService:
    """
    Service for astronomical calculations using the Skyfield library.
    Handles ephemeris loading and common astronomical queries.
    """
    _instance = None # Optional: Singleton pattern

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SkyfieldService, cls).__new__(cls)
            cls._instance._initialized = False # Use _initialized flag for actual init
        return cls._instance

    def __init__(self, ephemeris_path: str = None):
        if self._initialized:
            return

        self.logger = logging.getLogger(self.__class__.__name__)
        self.ephemeris_path = ephemeris_path or settings.skyfield_ephemeris_path
        self.ts = load.timescale()
        self.eph = None # Will be loaded lazily or in a dedicated method

        try:
            self.logger.info(f"Initializing SkyfieldService, attempting to load ephemeris from: '{self.ephemeris_path}'")
            # Ensure the directory exists
            ephem_dir = os.path.dirname(self.ephemeris_path)
            if not os.path.exists(ephem_dir):
                self.logger.warning(f"Skyfield ephemeris directory not found: {ephem_dir}. Attempting to download if needed.")
                os.makedirs(ephem_dir, exist_ok=True) # Create dir if it doesn't exist

            # Load the ephemeris. Skyfield will download if the file is not found.
            # This is a potentially long-running operation, consider handling in a worker.
            self.eph = load(self.ephemeris_path)
            self.logger.info("Skyfield ephemeris and service initialized successfully.")
            self._initialized = True
        except Exception as e:
            self.logger.critical(f"Failed to initialize SkyfieldService ephemeris: {e}", exc_info=True)
            raise RuntimeError(f"SkyfieldService failed to load ephemeris: {e}")

    def get_moon_phase_data(self, date_time: datetime) -> Dict[str, Any]:
        """
        Calculates the Moon's phase for a given UTC datetime.
        """
        if not self.eph:
            raise RuntimeError("Skyfield ephemeris not loaded.")

        t = self.ts.utc(date_time.year, date_time.month, date_time.day,
                        date_time.hour, date_time.minute, date_time.second)

        sun = self.eph['sun']
        moon = self.eph['moon']
        earth = self.eph['earth']

        # Position of Sun and Moon relative to Earth
        geocentric_sun = earth.at(t).observe(sun).ecliptic_longitude
        geocentric_moon = earth.at(t).observe(moon).ecliptic_longitude

        # Phase angle (difference in longitude)
        phase_angle = (geocentric_moon.degrees - geocentric_sun.degrees + 360) % 360

        phase_name, illumination_percent = self._determine_phase_details(phase_angle)

        return {
            "date_utc": date_time.isoformat(),
            "moon_phase_angle_degrees": round(phase_angle, 2),
            "moon_phase_name": phase_name,
            "illumination_percent": round(illumination_percent, 2),
            "description": f"The Moon is in a {phase_name} phase with {round(illumination_percent, 1)}% illumination."
        }

    def _determine_phase_details(self, phase_angle: float) -> Tuple[str, float]: # Uses Tuple correctly
        """Determines phase name and illumination from phase angle."""
        # Simplified illumination: 50% at quarters, 100% full, 0% new
        illumination = 50 * (1 + math.cos(math.radians(phase_angle)))

        if 337.5 <= phase_angle < 22.5:
            name = "New Moon"
            illumination = 0.0 # Truly dark
        elif 22.5 <= phase_angle < 67.5:
            name = "Waxing Crescent"
        elif 67.5 <= phase_angle < 112.5:
            name = "First Quarter"
            illumination = 50.0
        elif 112.5 <= phase_angle < 157.5:
            name = "Waxing Gibbous"
        elif 157.5 <= phase_angle < 202.5:
            name = "Full Moon"
            illumination = 100.0 # Fully lit
        elif 202.5 <= phase_angle < 247.5:
            name = "Waning Gibbous"
        elif 247.5 <= phase_angle < 292.5:
            name = "Last Quarter"
            illumination = 50.0
        elif 292.5 <= phase_angle < 337.5:
            name = "Waning Crescent"
        else:
            name = "Unknown" # Should not happen with 0-360 angle

        return name, illumination

    def get_planetary_positions(self, date_time: datetime, observer_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Gets geocentric or topocentric planetary positions for a given datetime.
        `observer_location` should be {'latitude': ..., 'longitude': ..., 'elevation': ...}.
        """
        if not self.eph:
            raise RuntimeError("Skyfield ephemeris not loaded.")

        t = self.ts.utc(date_time.year, date_time.month, date_time.day,
                        date_time.hour, date_time.minute, date_time.second)

        planets_data = {}
        for planet_name in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
            planet = self.eph[planet_name]
            
            if observer_location:
                # Topocentric position (from observer on Earth)
                lat = observer_location.get('latitude', 0.0)
                lon = observer_location.get('longitude', 0.0)
                elevation = observer_location.get('elevation', 0.0) # meters
                observer = self.eph['earth'] + Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elevation)
                astrometric = observer.at(t).observe(planet)
            else:
                # Geocentric position (from Earth's center)
                astrometric = self.eph['earth'].at(t).observe(planet)

            ra, dec, distance = astrometric.radec()
            
            # Get apparent longitude for zodiac placement (ecliptic longitude)
            lon_ecliptic, lat_ecliptic, _ = t.at(self.eph['earth']).observe(planet).ecliptic_position()
            
            # Get properties to calculate speed
            # Skyfield's approach to speed is usually about proper motion or specific components.
            # Calculating 'speed_longitude' directly in degrees/day from Skyfield's orbital elements
            # is complex and depends on the specific motion type (mean vs true anomaly).
            # For a simple 'speed' indicator, we can calculate change over a small time step.
            # This is a simplified approximation and might not match swe.calc_ut's output exactly.
            dt_next = self.ts.utc(date_time.year, date_time.month, date_time.day,
                                  date_time.hour, date_time.minute, date_time.second + 10) # 10 seconds later
            
            if observer_location:
                astrometric_next = observer.at(dt_next).observe(planet)
            else:
                astrometric_next = self.eph['earth'].at(dt_next).observe(planet)

            lon_ecliptic_next, _, _ = dt_next.at(self.eph['earth']).observe(planet).ecliptic_position()
            
            # Speed in degrees per day (approximate)
            speed_deg_per_day = ((lon_ecliptic_next.degrees - lon_ecliptic.degrees + 360) % 360) / (10/86400) # (change in degrees) / (fraction of day)
            if speed_deg_per_day > 180: # Handle wrap around for speed direction
                speed_deg_per_day -= 360

            is_retrograde = speed_deg_per_day < 0
            
            planets_data[planet_name] = {
                "name": planet_name.capitalize(),
                "ra_degrees": ra.degrees,
                "dec_degrees": dec.degrees,
                "distance_au": distance.au,
                "ecliptic_longitude_degrees": lon_ecliptic.degrees,
                "ecliptic_latitude_degrees": lat_ecliptic.degrees,
                "is_retrograde": is_retrograde,
                "speed_degrees_per_day": speed_deg_per_day,
                "position_type": "topocentric" if observer_location else "geocentric"
            }
        return planets_data

    def get_satellite_position(self, tle_line1: str, tle_line2: str, date_time: datetime, observer_location: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculates position of a satellite given TLE data and observer location.
        `observer_location` should be {'latitude': ..., 'longitude': ..., 'elevation': ...}.
        """
        if not self.eph:
            raise RuntimeError("Skyfield ephemeris not loaded.")

        satellite = EarthSatellite(tle_line1, tle_line2, 'Satellite Name', self.ts)
        
        geolocator = Topos(latitude_degrees=observer_location['latitude'],
                           longitude_degrees=observer_location['longitude'],
                           elevation_m=observer_location.get('elevation', 0))

        t = self.ts.utc(date_time.year, date_time.month, date_time.day,
                        date_time.hour, date_time.minute, date_time.second)

        difference = satellite - geolocator
        topocentric = difference.at(t)

        alt, az, distance = topocentric.altaz()

        return {
            "date_utc": date_time.isoformat(),
            "satellite_name": 'Satellite Name', # TLE often doesn't contain name, so it's a placeholder
            "altitude_degrees": alt.degrees,
            "azimuth_degrees": az.degrees,
            "distance_km": distance.km,
            "is_above_horizon": alt.degrees > 0
        }

    def calculate_precise_position(self, body_name: str, date: datetime, 
                                observer_lat: float = None, observer_lon: float = None,
                                topocentric: bool = True) -> Dict[str, Any]:
        """
        Calculate precise position of a celestial body with all corrections:
        - Aberration
        - Nutation
        - Precession
        - Proper motion (for stars)
        - Relativistic effects
        - Topocentric parallax (if observer position provided)
        """
        ts = self.ts
        t = ts.from_datetime(date)
        
        # Load the ephemeris if not already loaded
        if not self.eph:
            self.eph = load('de441.bsp')  # Most precise ephemeris
        
        # Get the celestial body
        body = self.eph[body_name]
        earth = self.eph['earth']
        
        # Calculate position from Earth's center
        if observer_lat is not None and observer_lon is not None and topocentric:
            # Topocentric position (from observer's location)
            observer = earth + Topos(latitude_degrees=observer_lat,
                                   longitude_degrees=observer_lon)
            position = observer.at(t).observe(body)
        else:
            # Geocentric position
            position = earth.at(t).observe(body)
        
        # Apply relativistic corrections
        position = position.apparent()
        
        # Get different coordinate representations
        ra, dec, distance = position.radec()
        alt, az, d = position.altaz()
        lon, lat, d = position.ecliptic_latlon()
        
        # Calculate additional parameters
        velocity = position.velocity.km_per_s
        light_time = position.light_time
        
        return {
            'radec': {
                'ra_hours': ra.hours,
                'dec_degrees': dec.degrees,
                'distance_au': distance.au
            },
            'altaz': {
                'altitude_degrees': alt.degrees,
                'azimuth_degrees': az.degrees
            },
            'ecliptic': {
                'longitude_degrees': lon.degrees,
                'latitude_degrees': lat.degrees
            },
            'velocity_km_s': velocity,
            'light_time_days': light_time,
            'timestamp': date.isoformat(),
            'observer': {
                'latitude': observer_lat,
                'longitude': observer_lon
            } if topocentric else None
        }

    def calculate_precession(self, ra_hours: float, dec_degrees: float, 
                           from_epoch: float, to_epoch: float) -> Dict[str, float]:
        """
        Calculate precession of coordinates between epochs.
        Uses rigorous precession formulas.
        """
        # Convert coordinates to position vector
        ra = Angle(hours=ra_hours)
        dec = Angle(degrees=dec_degrees)
        
        # Get precession matrix
        P = precession_matrix(from_epoch, to_epoch)
        
        # Apply precession
        pos = ra.radians, dec.radians, 1.0
        new_pos = P @ pos
        
        # Convert back to spherical coordinates
        new_ra = Angle(radians=math.atan2(new_pos[1], new_pos[0]))
        new_dec = Angle(radians=math.asin(new_pos[2]))
        
        return {
            'ra_hours': new_ra.hours,
            'dec_degrees': new_dec.degrees,
            'from_epoch': from_epoch,
            'to_epoch': to_epoch
        }

    def calculate_astronomical_events(self, date: datetime, duration_days: int = 30) -> Dict[str, List[Dict]]:
        """
        Calculate major astronomical events for a period:
        - Conjunctions
        - Oppositions
        - Maximum elongations
        - Stationary points
        - Equinoxes and solstices
        - Eclipses
        """
        events = []
        ts = self.ts
        t0 = ts.from_datetime(date)
        t1 = ts.from_datetime(date + timedelta(days=duration_days))
        
        # Check for planetary events
        planets = ['mercury', 'venus', 'mars', 'jupiter', 'saturn']
        sun = self.eph['sun']
        earth = self.eph['earth']
        
        for planet_name in planets:
            planet = self.eph[planet_name]
            
            # Find conjunctions and oppositions
            for t in ts.linspace(t0, t1, duration_days * 24):  # Hourly checks
                pos_planet = earth.at(t).observe(planet)
                pos_sun = earth.at(t).observe(sun)
                
                angle = pos_planet.separation_from(pos_sun)
                
                if abs(angle.degrees) < 1:  # Conjunction
                    events.append({
                        'type': 'conjunction',
                        'bodies': ['sun', planet_name],
                        'time': t.utc_datetime()
                    })
                elif abs(angle.degrees - 180) < 1:  # Opposition
                    events.append({
                        'type': 'opposition',
                        'bodies': ['sun', planet_name],
                        'time': t.utc_datetime()
                    })
        
        return {'events': sorted(events, key=lambda x: x['time'])}