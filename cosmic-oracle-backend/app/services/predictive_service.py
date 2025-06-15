# app/services/predictive_service.py
"""
Predictive Astrology Service

This service provides predictive astrological calculations, including planetary
transits and secondary progressions, to analyze current and future trends
based on a natal chart.
"""
import logging
import datetime
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# --- REUSE: Import existing services and utilities ---
from app.services.astrology_service import get_natal_chart_details, astro_data_cache, parse_datetime_with_timezone, convert_to_utc

logger = logging.getLogger(__name__)

class PredictiveService:
    def __init__(self, astronomical_service):
        self.astronomical = astronomical_service

# --- Transit Calculation Logic ---
    def _calculate_transit_aspects(self, natal_chart: Dict[str, Any], transit_chart: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Private helper to calculate aspects between transiting planets and natal planets/angles.

        Args:
            natal_chart: Dictionary containing the natal chart data
            transit_chart: Dictionary containing the transit chart data

        Returns:
            List of aspect dictionaries
        """
        aspect_list = []
        transiting_points = list(transit_chart['points'].values())
        natal_points = list(natal_chart['points'].values()) + list(natal_chart['angles'].values())
        aspect_definitions = astro_data_cache.aspects

        for t_point in transiting_points:
            # We only care about transits from the 10 traditional planets
            if t_point['name'] not in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
                continue
                
            for n_point in natal_points:
                separation = abs(t_point['longitude'] - n_point['longitude'])
                if separation > 180:
                    separation = 360 - separation

                for aspect_name, aspect_info in aspect_definitions.items():
                    # For transits, we use a much tighter orb, typically 1 degree.
                    if abs(separation - aspect_info["degrees"]) <= 1.5:
                        aspect_list.append({
                            "transiting_planet": t_point['name'],
                            "natal_point": n_point['name'],
                            "aspect_name": aspect_name,
                            "aspect_symbol": aspect_info["symbol"],
                            "orb_degrees": round(abs(separation - aspect_info["degrees"]), 3),
                        })
        
        return sorted(aspect_list, key=lambda x: x['orb_degrees'])

    def analyze_transits(
        self,
        natal_chart_data: Dict[str, Any],
        transit_datetime_str: str,
        timezone_str: str,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Public facade for analyzing transits for a given moment.

        Args:
            natal_chart_data: A dictionary containing the user's birth data.
            transit_datetime_str: The date to calculate transits for.
            timezone_str: The timezone for the transit date.
            latitude: The location for which to calculate the transit chart angles.
            longitude: The longitude for the transit chart angles.
        
        Returns:
            A dictionary containing the transit analysis or an error.
        """
        logger.info(f"Predictive service: calculating transits for {transit_datetime_str}.")
        try:
            # Step 1: Generate the user's natal chart.
            natal_chart = get_natal_chart_details(**natal_chart_data)
            if 'error' in natal_chart:
                return {"error": f"Could not calculate base natal chart: {natal_chart['error']}"}

            # Step 2: Generate the chart for the transit moment.
            transit_chart = get_natal_chart_details(
                datetime_str=transit_datetime_str,
                timezone_str=timezone_str,
                latitude=latitude,
                longitude=longitude,
                house_system="Placidus"
            )
            if 'error' in transit_chart:
                return {"error": f"Could not calculate transit chart: {transit_chart['error']}"}

            # Step 3: Perform the transit calculations.
            transit_aspects = self._calculate_transit_aspects(natal_chart, transit_chart)

            return {
                "predictive_analysis": {
                    "type": "Transits",
                    "transit_date_utc": transit_chart['chart_info']['datetime_utc'],
                    "active_transit_aspects": transit_aspects,
                },
                "transit_chart_positions": transit_chart['points'],
                "natal_chart_used": natal_chart['chart_info'],
            }

        except Exception as e:
            logger.critical(f"An unexpected fatal error occurred in the transit service: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred during transit analysis."}


# --- Secondary Progression Logic ---
    def analyze_secondary_progressions(
        self,
        natal_chart_data: Dict[str, Any],
        target_age: int
    ) -> Dict[str, Any]:
        """
        Public facade for calculating a secondary progressed chart for a given age.
        "A day for a year" - the chart for the Nth day after birth represents the Nth year of life.
        """
        logger.info(f"Predictive service: calculating secondary progressions for age {target_age}.")
        try:
            # Step 1: Parse the user's birth datetime.
            birth_dt_aware = parse_datetime_with_timezone(
                natal_chart_data['datetime_str'],
                natal_chart_data['timezone_str']
            )
            if not birth_dt_aware:
                return {"error": "Invalid birth data provided."}

            # Step 2: Calculate the progressed date (N days after birth for Nth year).
            progressed_dt_aware = birth_dt_aware + datetime.timedelta(days=target_age)
            
            # Step 3: Generate the chart for the progressed moment. Location remains the same as birth.
            progressed_chart = get_natal_chart_details(
                datetime_str=progressed_dt_aware.isoformat(),
                timezone_str=natal_chart_data['timezone_str'], # Keep original timezone for correct UTC conversion
                latitude=natal_chart_data['latitude'],
                longitude=natal_chart_data['longitude'],
                house_system="Placidus"
            )
            if 'error' in progressed_chart:
                return {"error": f"Could not calculate progressed chart: {progressed_chart['error']}"}

            # Step 4: A full analysis would compare this chart to the natal chart.
            # For now, we return the positions of the progressed planets.
            # The most important is the Progressed Moon.
            prog_moon = progressed_chart['points']['Moon']

            return {
                "predictive_analysis": {
                    "type": "Secondary Progressions",
                    "target_age": target_age,
                    "progressed_date_for_calculation": progressed_dt_aware.isoformat(),
                    "progressed_moon_position": f"{int(prog_moon['degrees_in_sign'])}° {prog_moon['sign_name']} in House {prog_moon['house']}"
                },
                "progressed_chart_positions": progressed_chart['points']
            }

        except Exception as e:
            logger.critical(f"An unexpected fatal error occurred in the progressions service: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred during progression analysis."}

# --- Advanced Predictive Techniques ---
    def calculate_transits(self, birth_chart: Dict[str, Any],
                         start_date: datetime,
                         end_date: datetime,
                         orb: float = 1.0) -> List[Dict[str, Any]]:
        """Calculate exact transit times with high precision."""
        transits = []
        check_points = ['sun', 'moon', 'mercury', 'venus', 'mars',
                       'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        
        # Define major aspects to check
        aspects = {
            0: 'conjunction',
            60: 'sextile',
            90: 'square',
            120: 'trine',
            180: 'opposition'
        }
        
        current = start_date
        while current <= end_date:
            # Get transit positions
            transit_positions = {}
            for planet in check_points:
                pos = self.astronomical.get_planet_position(planet, current)
                transit_positions[planet] = pos
            
            # Check aspects to natal planets
            for tr_planet, tr_pos in transit_positions.items():
                for natal_planet, natal_pos in birth_chart['planets'].items():
                    # Calculate angular separation
                    diff = abs(tr_pos['longitude'] - natal_pos['longitude'])
                    if diff > 180:
                        diff = 360 - diff
                    
                    # Check each aspect
                    for aspect_deg, aspect_name in aspects.items():
                        if abs(diff - aspect_deg) < orb:
                            # Found an aspect - calculate exact timing
                            exact_time = self._find_exact_aspect_time(
                                tr_planet, natal_planet,
                                natal_pos['longitude'],
                                current, aspect_deg
                            )
                            
                            transits.append({
                                'transit_planet': tr_planet,
                                'natal_planet': natal_planet,
                                'aspect': aspect_name,
                                'aspect_degree': aspect_deg,
                                'exact_time': exact_time,
                                'orb': abs(diff - aspect_deg),
                                'transit_speed': tr_pos['speed'],
                                'is_applying': self._is_aspect_applying(
                                    tr_pos['speed'],
                                    tr_pos['longitude'],
                                    natal_pos['longitude'],
                                    aspect_deg
                                )
                            })
            
            current += timedelta(hours=1)
        
        return sorted(transits, key=lambda x: x['exact_time'])

    def _find_exact_aspect_time(self,
                             transit_planet: str,
                             natal_planet: str,
                               natal_longitude: float,
                               approx_time: datetime,
                               aspect_degree: float,
                               precision: float = 0.0001) -> datetime:
        """Find exact time of aspect using binary search."""
        lower = approx_time - timedelta(hours=12)
        upper = approx_time + timedelta(hours=12)
        
        while (upper - lower) > timedelta(seconds=1):
            mid = lower + (upper - lower) / 2
            pos = self.astronomical.get_planet_position(transit_planet, mid)
            
            diff = abs(pos['longitude'] - natal_longitude)
            if diff > 180:
                diff = 360 - diff
                
            if abs(diff - aspect_degree) < precision:
                return mid
                
            if diff < aspect_degree:
                lower = mid
            else:
                upper = mid
        
        return lower

    def _is_aspect_applying(transit_speed: float,
                           transit_lon: float,
                           natal_lon: float,
                           aspect_degree: float) -> bool:
        """Determine if an aspect is applying or separating."""
        # Calculate shortest distance between the points
        diff = transit_lon - natal_lon
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        # For aspects other than conjunction
        if aspect_degree > 0:
            target_diff = aspect_degree
            if diff > 0:
                target_diff = -aspect_degree
        else:
            target_diff = 0
        
        # If moving towards the aspect
        if abs(diff - target_diff) > abs(diff + transit_speed - target_diff):
            return True
        return False

    def calculate_eclipse_series(start_date: datetime,
                               end_date: datetime) -> List[Dict[str, Any]]:
        """Calculate all eclipses in a period with Saros cycle information."""
        eclipses = []
        current = start_date
        
        while current <= end_date:
            # Check for solar eclipse
            solar = self.astronomical.calculate_next_eclipse(current)
            if solar['next_solar_eclipse']['date'] <= end_date:
                # Calculate Saros series
                saros_data = self._calculate_saros_number(
                    solar['next_solar_eclipse']['date'],
                    True  # is_solar
                )
                
                eclipses.append({
                    'type': 'solar',
                    'date': solar['next_solar_eclipse']['date'],
                    'eclipse_type': solar['next_solar_eclipse']['type'],
                    'saros_series': saros_data['series'],
                    'saros_number': saros_data['number']
                })
                current = solar['next_solar_eclipse']['date'] + timedelta(days=1)
            
            # Check for lunar eclipse
            lunar = self.astronomical.calculate_next_eclipse(current)
            if lunar['next_lunar_eclipse']['date'] <= end_date:
                saros_data = self._calculate_saros_number(
                    lunar['next_lunar_eclipse']['date'],
                    False  # is_solar
                )
                
                eclipses.append({
                    'type': 'lunar',
                    'date': lunar['next_lunar_eclipse']['date'],
                    'eclipse_type': lunar['next_lunar_eclipse']['type'],
                    'saros_series': saros_data['series'],
                    'saros_number': saros_data['number']
                })
                current = lunar['next_lunar_eclipse']['date'] + timedelta(days=1)
            
            current += timedelta(days=1)
        
        return sorted(eclipses, key=lambda x: x['date'])

    def _calculate_saros_number(eclipse_date: datetime,
                            is_solar: bool) -> Dict[str, int]:
        """Calculate Saros series and number for an eclipse."""
        # Saros cycle is approximately 6585.3211 days
        SAROS_DAYS = 6585.3211
        
        # Reference eclipse (Saros 1)
        if is_solar:
            reference_date = datetime(1685, 2, 22)  # Saros 1 started
        else:
            reference_date = datetime(1685, 2, 8)   # Lunar Saros 1
        
        days_since_reference = (eclipse_date - reference_date).total_seconds() / 86400
        saros_cycles = days_since_reference / SAROS_DAYS
        
        # Calculate series number
        series = int(saros_cycles) + 1
        
        # Calculate where in the series this eclipse falls
        number = int((saros_cycles % 1) * 75) + 1  # Each series has about 75 eclipses
        
        return {
            'series': series,
            'number': number
        }