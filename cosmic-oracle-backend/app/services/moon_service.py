# app/services/moon_service.py
"""
Moon Phase and Lunar Astrology Service

This service provides functions to calculate moon phases, retrieve moon
interpretations, and potentially offer lunar insights.
"""
import logging
import math
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple # Ensure all typing hints are imported

# Import the ContentFetchService CLASS, not standalone functions
from app.services.content_fetch_service import ContentFetchService 

# For astronomical calculations, using SkyfieldService
from app.services.skyfield_service import SkyfieldService
from app.services.lunar_mansion_service import lunar_mansion_service_instance

logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class MoonService:
    _instance = None # Optional: For singleton pattern if desired

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MoonService, cls).__new__(cls)
        return cls._instance

    def __init__(self, content_fetch_service_instance: ContentFetchService = None, skyfield_service_instance: SkyfieldService = None):
        if hasattr(self, '_initialized') and self._initialized:
            return

        logger.info("Initializing MoonService...")

        # IMPORTANT: Receive service instances via constructor
        if content_fetch_service_instance is None:
            raise RuntimeError("ContentFetchService instance must be provided to MoonService.")
        self.content_fetch_service = content_fetch_service_instance
        
        # Initialize SkyfieldService for astronomical calculations
        if skyfield_service_instance is None:
            try:
                self.skyfield_service = SkyfieldService()
            except Exception as e:
                logger.error(f"Failed to initialize SkyfieldService: {e}")
                self.skyfield_service = None
        else:
            self.skyfield_service = skyfield_service_instance

        # Load moon content and zodiac data via the injected content_fetch_service
        self.moon_content = self.content_fetch_service.get_moon_content() # Now a method call
        self.zodiac_data = self.content_fetch_service.get_zodiac_signs_data() # Now a method call

        if not self.moon_content or not self.zodiac_data:
            raise RuntimeError("Could not load necessary moon or zodiac content files from content_fetch_service.")
        
        self._initialized = True
        logger.info("MoonService initialized successfully.")

    def get_moon_phase(self, datetime_utc: datetime) -> Dict[str, Any]:
        """
        Calculates the moon phase for a given UTC datetime using Skyfield astronomical calculations.
        """
        if self.skyfield_service:
            try:
                # Get accurate moon phase data from Skyfield
                moon_phase_data = self.skyfield_service.get_moon_phase_data(datetime_utc)
                
                # Add interpretation from content
                phase_name = moon_phase_data.get('moon_phase_name', 'Unknown Phase')
                phase_key = phase_name.lower().replace(' ', '_')
                interpretation = self.moon_content.get('phases', {}).get(phase_key, "No specific interpretation available.")
                moon_phase_data['interpretation'] = interpretation
                
                return moon_phase_data
                
            except Exception as e:
                logger.error(f"Error calculating moon phase with Skyfield: {e}")
                # Fall back to approximate calculation
                return self._get_approximate_moon_phase(datetime_utc)
        else:
            logger.warning("SkyfieldService not available, using approximate calculation.")
            return self._get_approximate_moon_phase(datetime_utc)

    def _get_approximate_moon_phase(self, datetime_utc: datetime) -> Dict[str, Any]:
        """
        Fallback approximate moon phase calculation when Skyfield is not available.
        """
        # Simplified approximation based on lunar cycle
        jd = datetime_utc.toordinal() + 1721424.5 - 2451545.0
        days_into_cycle = jd % 29.53058867
        
        if 28 <= days_into_cycle or days_into_cycle < 1.5:
            phase_name = "New Moon"
            illumination = 0.0
        elif 1.5 <= days_into_cycle < 6.5:
            phase_name = "Waxing Crescent"
            illumination = 25.0
        elif 6.5 <= days_into_cycle < 9.5:
            phase_name = "First Quarter"
            illumination = 50.0
        elif 9.5 <= days_into_cycle < 13.5:
            phase_name = "Waxing Gibbous"
            illumination = 75.0
        elif 13.5 <= days_into_cycle < 16.5:
            phase_name = "Full Moon"
            illumination = 100.0
        elif 16.5 <= days_into_cycle < 21.5:
            phase_name = "Waning Gibbous"
            illumination = 75.0
        elif 21.5 <= days_into_cycle < 25.5:
            phase_name = "Last Quarter"
            illumination = 50.0
        elif 25.5 <= days_into_cycle < 28:
            phase_name = "Waning Crescent"
            illumination = 25.0
        else:
            phase_name = "Unknown"
            illumination = 0.0

        # Fetch interpretation from loaded content
        phase_key = phase_name.lower().replace(' ', '_')
        interpretation = self.moon_content.get('phases', {}).get(phase_key, "No specific interpretation available.")
        
        return {
            "date_utc": datetime_utc.isoformat(),
            "moon_phase_name": phase_name,
            "interpretation": interpretation,
            "illumination_percent": illumination,
            "description": f"The Moon is in a {phase_name} phase with approximately {illumination}% illumination."
        }


    def get_moon_in_zodiac(self, datetime_utc: datetime) -> Dict[str, Any]:
        """
        Determines the zodiac sign the Moon is currently transiting using Skyfield calculations.
        """
        if self.skyfield_service:
            try:
                # Get accurate planetary positions from Skyfield
                planetary_positions = self.skyfield_service.get_planetary_positions(datetime_utc)
                moon_data = planetary_positions.get('moon', {})
                moon_lon = moon_data.get('ecliptic_longitude_degrees')
                
                if moon_lon is None:
                    logger.error("Failed to get Moon's longitude from Skyfield")
                    return self._get_approximate_moon_in_zodiac(datetime_utc)
                
                # Calculate zodiac sign from longitude
                moon_sign_index = int(moon_lon // 30)
                moon_sign_key = list(self.zodiac_data.keys())[moon_sign_index]
                moon_sign_info = self.zodiac_data.get(moon_sign_key)
                
                if moon_sign_info:
                    interpretation = self.moon_content.get('moon_in_signs', {}).get(moon_sign_key, "No specific interpretation available.")
                    return {
                        "date_utc": datetime_utc.isoformat(),
                        "moon_longitude": round(moon_lon, 4),
                        "moon_sign_name": moon_sign_info.get('name'),
                        "moon_sign_key": moon_sign_key,
                        "interpretation": interpretation,
                        "is_retrograde": moon_data.get('is_retrograde', False),
                        "speed_degrees_per_day": moon_data.get('speed_degrees_per_day', 0.0)
                    }
                else:
                    return {"error": "Could not determine moon sign or its data."}
                    
            except Exception as e:
                logger.error(f"Error calculating Moon's zodiac position with Skyfield: {e}")
                return self._get_approximate_moon_in_zodiac(datetime_utc)
        else:
            logger.warning("SkyfieldService not available, using approximate calculation.")
            return self._get_approximate_moon_in_zodiac(datetime_utc)

    def _get_approximate_moon_in_zodiac(self, datetime_utc: datetime) -> Dict[str, Any]:
        """
        Fallback approximate Moon in zodiac calculation when Skyfield is not available.
        """
        # Very rough approximation for fallback
        mock_moon_lon = (datetime_utc.day * 10 + datetime_utc.hour * 0.5) % 360
        moon_sign_index = int(mock_moon_lon // 30)
        
        moon_sign_key = list(self.zodiac_data.keys())[moon_sign_index]
        moon_sign_info = self.zodiac_data.get(moon_sign_key)
        
        if moon_sign_info:
            interpretation = self.moon_content.get('moon_in_signs', {}).get(moon_sign_key, "No specific interpretation available.")
            return {
                "date_utc": datetime_utc.isoformat(),
                "moon_longitude": round(mock_moon_lon, 4),
                "moon_sign_name": moon_sign_info.get('name'),
                "moon_sign_key": moon_sign_key,
                "interpretation": interpretation,
                "note": "Approximate calculation - Skyfield service unavailable"
            }
        else:
            return {"error": "Could not determine moon sign or its data."}

    def get_lunar_mansion(self, datetime_utc: datetime) -> Dict[str, Any]:
        """
        Calculates the current Lunar Mansion (Nakshatra) for the given datetime.
        """
        if lunar_mansion_service_instance:
            try:
                return lunar_mansion_service_instance.get_current_mansion(datetime_utc)
            except Exception as e:
                logger.error(f"Error calculating lunar mansion: {e}")
                return {"error": f"Failed to calculate lunar mansion: {str(e)}"}
        else:
            return {"error": "Lunar mansion service not available"}

    def get_moon_void_of_course(self, datetime_utc: datetime) -> Dict[str, Any]:
        """
        Determines if the Moon is void of course at the given time.
        Moon is void of course when it makes no more major aspects before changing signs.
        """
        if not self.skyfield_service:
            return {"error": "Skyfield service required for void of course calculations"}
        
        try:
            # Get current Moon position
            planetary_positions = self.skyfield_service.get_planetary_positions(datetime_utc)
            moon_data = planetary_positions.get('moon', {})
            moon_lon = moon_data.get('ecliptic_longitude_degrees')
            
            if moon_lon is None:
                return {"error": "Failed to get Moon's longitude"}
            
            # Calculate when Moon enters next sign (simplified)
            current_sign = int(moon_lon // 30)
            next_sign_start = (current_sign + 1) * 30
            degrees_to_next_sign = (next_sign_start - moon_lon) % 360
            
            # Estimate time to next sign based on Moon's average speed (~13 degrees/day)
            avg_moon_speed = 13.176  # degrees per day
            hours_to_next_sign = (degrees_to_next_sign / avg_moon_speed) * 24
            
            return {
                "date_utc": datetime_utc.isoformat(),
                "moon_longitude": round(moon_lon, 4),
                "current_sign_number": current_sign + 1,
                "degrees_to_next_sign": round(degrees_to_next_sign, 4),
                "estimated_hours_to_next_sign": round(hours_to_next_sign, 2),
                "note": "Simplified void of course calculation - full aspect analysis requires more complex computation"
            }
            
        except Exception as e:
            logger.error(f"Error calculating void of course: {e}")
            return {"error": f"Failed to calculate void of course: {str(e)}"}

    def get_moon_nodes(self, datetime_utc: datetime) -> Dict[str, Any]:
        """
        Calculates the position of the lunar nodes (North Node/Rahu and South Node/Ketu).
        """
        if not self.skyfield_service:
            return {"error": "Skyfield service required for lunar node calculations"}
        
        try:
            # Calculate lunar nodes using orbital mechanics
            # This is a simplified calculation - full precision requires more complex computation
            t = self.skyfield_service.ts.utc(
                datetime_utc.year, datetime_utc.month, datetime_utc.day,
                datetime_utc.hour, datetime_utc.minute, datetime_utc.second
            )
            
            # Get Moon's position
            moon = self.skyfield_service.eph['moon']
            earth = self.skyfield_service.eph['earth']
            
            # Calculate approximate lunar node positions
            # True node calculation requires orbital elements
            astrometric = earth.at(t).observe(moon)
            lon, lat, _ = astrometric.ecliptic_position()
            
            # Simplified node calculation (this is approximate)
            # For accurate nodes, we'd need to access Moon's orbital elements
            mean_node_lon = (125.04452 - 1934.136261 * ((t.tt - 2451545.0) / 36525)) % 360
            
            # North Node (Rahu)
            north_node_sign_index = int(mean_node_lon // 30)
            north_node_sign_key = list(self.zodiac_data.keys())[north_node_sign_index]
            north_node_sign_info = self.zodiac_data.get(north_node_sign_key, {})
            
            # South Node (Ketu) is exactly opposite (180 degrees)
            south_node_lon = (mean_node_lon + 180) % 360
            south_node_sign_index = int(south_node_lon // 30)
            south_node_sign_key = list(self.zodiac_data.keys())[south_node_sign_index]
            south_node_sign_info = self.zodiac_data.get(south_node_sign_key, {})
            
            return {
                "date_utc": datetime_utc.isoformat(),
                "north_node": {
                    "longitude": round(mean_node_lon, 4),
                    "sign_name": north_node_sign_info.get('name', 'Unknown'),
                    "sign_key": north_node_sign_key,
                    "degrees_in_sign": round(mean_node_lon % 30, 4)
                },
                "south_node": {
                    "longitude": round(south_node_lon, 4),
                    "sign_name": south_node_sign_info.get('name', 'Unknown'),
                    "sign_key": south_node_sign_key,
                    "degrees_in_sign": round(south_node_lon % 30, 4)
                },
                "note": "Simplified node calculation using mean node formula"
            }
            
        except Exception as e:
            logger.error(f"Error calculating lunar nodes: {e}")
            return {"error": f"Failed to calculate lunar nodes: {str(e)}"}

    def get_comprehensive_moon_data(self, datetime_utc: datetime) -> Dict[str, Any]:
        """
        Returns comprehensive moon data including phase, zodiac position, mansion, and nodes.
        """
        try:
            moon_phase = self.get_moon_phase(datetime_utc)
            moon_zodiac = self.get_moon_in_zodiac(datetime_utc)
            lunar_mansion = self.get_lunar_mansion(datetime_utc)
            void_of_course = self.get_moon_void_of_course(datetime_utc)
            lunar_nodes = self.get_moon_nodes(datetime_utc)
            
            return {
                "calculation_datetime_utc": datetime_utc.isoformat(),
                "moon_phase": moon_phase,
                "moon_in_zodiac": moon_zodiac,
                "lunar_mansion": lunar_mansion,
                "void_of_course": void_of_course,
                "lunar_nodes": lunar_nodes
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive moon data: {e}")
            return {"error": f"Failed to get comprehensive moon data: {str(e)}"}

    def calculate_lunar_phenomena(self, date: datetime) -> Dict[str, Any]:
        """Calculate advanced lunar phenomena including:
        - Precise phase angle and illumination
        - Distance from Earth (in km)
        - Angular size (in arc minutes)
        - Libration in latitude and longitude
        - Subsolar point
        - Ascending/descending node crossings
        """
        ts = self.skyfield_service.ts
        t = ts.from_datetime(date)
        
        # Get Earth and Moon positions
        earth = self.skyfield_service.eph['earth']
        moon = self.skyfield_service.eph['moon']
        
        # Calculate Earth-Moon distance and angular size
        earth_moon = earth.at(t).observe(moon)
        distance = earth_moon.distance().km
        angular_size = math.degrees(math.atan2(1737.1, distance)) * 60  # Moon's radius is 1737.1 km

        # Calculate libration
        _, lon_lib, lat_lib = earth_moon.frame_latlon(center=moon)
        
        # Get phase information
        phase_angle = earth_moon.phase_angle()
        illumination = (1 + math.cos(phase_angle.radians)) / 2

        # Calculate nodes (simplified for example)
        nodes = self._calculate_lunar_nodes(t)

        return {
            'phase_angle_degrees': phase_angle.degrees,
            'illumination_percentage': illumination * 100,
            'distance_km': distance,
            'angular_size_arcmin': angular_size,
            'libration': {
                'longitude_degrees': lon_lib.degrees,
                'latitude_degrees': lat_lib.degrees
            },
            'nodes': nodes,
            'timestamp': date.isoformat()
        }

    def _calculate_lunar_nodes(self, t: 'Time') -> Dict[str, Any]:
        """Calculate lunar node information"""
        earth = self.skyfield_service.eph['earth']
        moon = self.skyfield_service.eph['moon']
        
        # Get Moon's position relative to Earth
        pos = earth.at(t).observe(moon)
        
        # Convert to ecliptic coordinates
        ecliptic = pos.ecliptic_latlon()
        lat = ecliptic[1].degrees
        
        # Find approximate node crossings
        if abs(lat) < 1.0:  # Near a node
            lon = ecliptic[0].degrees
            node_type = "ascending" if lat > 0 else "descending"
            return {
                'type': node_type,
                'longitude': lon,
                'latitude': lat
            }
        return {'type': 'none', 'longitude': None, 'latitude': None}

    def calculate_lunar_mansion(self, date: datetime) -> Dict[str, Any]:
        """Calculate traditional lunar mansion (nakshatra)"""
        ts = self.skyfield_service.ts
        t = ts.from_datetime(date)
        
        earth = self.skyfield_service.eph['earth']
        moon = self.skyfield_service.eph['moon']
        
        # Get Moon's position
        pos = earth.at(t).observe(moon)
        lon = pos.ecliptic_latlon()[0].degrees
        
        # Calculate mansion number (27 mansions system)
        mansion_number = int((lon % 360) / (360/27)) + 1
        
        # Get traditional interpretations
        mansion_data = self.content_fetch_service.get_lunar_mansion_data(mansion_number)
        
        return {
            'mansion_number': mansion_number,
            'longitude': lon,
            'name': mansion_data.get('name', ''),
            'symbol': mansion_data.get('symbol', ''),
            'interpretation': mansion_data.get('interpretation', ''),
            'timestamp': date.isoformat()
        }