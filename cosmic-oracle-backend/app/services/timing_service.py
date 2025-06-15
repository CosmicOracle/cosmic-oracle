"""
Advanced Astrological Timing Service

This service handles complex astrological timing techniques including:
- Time lord systems (Firdaria, Decennials, etc.)
- Primary directions
- Solar and lunar returns
- Profections
- Zodiacal releasing
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math
from dataclasses import dataclass

from app.services.astronomical_service import AstronomicalService
from app.services.skyfield_service import SkyfieldService

logger = logging.getLogger(__name__)

@dataclass
class PrimaryDirection:
    significator: str  # Planet or point being directed
    promissor: str    # Planet or point being directed to
    arc_degrees: float
    mundane: bool     # True for mundane directions, False for zodiacal
    converse: bool    # True for converse directions

class AstrologicalTimingService:
    """Handles advanced astrological timing techniques."""
    
    def __init__(self, astronomical_service: AstronomicalService,
                 skyfield_service: SkyfieldService):
        self.astronomical = astronomical_service
        self.skyfield = skyfield_service
        
    def calculate_solar_return(self, birth_date: datetime,
                             target_year: int,
                             lat: float = None,
                             lon: float = None) -> Dict[str, Any]:
        """Calculate precise solar return chart."""
        # Get birth solar longitude
        birth_sun = self.astronomical.get_planet_position('sun', birth_date)
        birth_sun_lon = birth_sun['longitude']
        
        # Find exact return time
        start_date = datetime(target_year, birth_date.month, birth_date.day)
        current_date = start_date - timedelta(days=5)  # Start 5 days before
        
        # Binary search for exact return
        while True:
            sun_pos = self.astronomical.get_planet_position('sun', current_date)
            diff = sun_pos['longitude'] - birth_sun_lon
            
            if abs(diff) < 0.000001:  # Extremely precise
                break
                
            if diff > 0:
                current_date -= timedelta(minutes=1)
            else:
                current_date += timedelta(minutes=1)
        
        # Calculate full chart for return moment
        return self.astronomical.calculate_birth_chart(
            current_date, lat or 0, lon or 0
        )
    
    def calculate_profections(self, birth_date: datetime,
                            target_date: datetime) -> Dict[str, Any]:
        """Calculate annual, monthly, and daily profections."""
        years = (target_date.year - birth_date.year +
                (target_date.month - birth_date.month)/12 +
                (target_date.day - birth_date.day)/365.25)
        
        # Annual profection (30 degrees per year)
        annual_shift = (years * 30) % 360
        annual_house = (int(annual_shift / 30) % 12) + 1
        
        # Monthly profection (2.5 degrees per month)
        months = years * 12
        monthly_shift = (months * 2.5) % 360
        monthly_house = (int(monthly_shift / 30) % 12) + 1
        
        # Daily profection
        days = (target_date - birth_date).days
        daily_shift = (days * 0.0821917808219178) % 360  # 360/365.25/12
        daily_house = (int(daily_shift / 30) % 12) + 1
        
        return {
            'annual': {
                'house': annual_house,
                'degrees': annual_shift
            },
            'monthly': {
                'house': monthly_house,
                'degrees': monthly_shift
            },
            'daily': {
                'house': daily_house,
                'degrees': daily_shift
            }
        }
    
    def calculate_firdaria(self, birth_date: datetime,
                          is_diurnal: bool) -> List[Dict[str, Any]]:
        """Calculate Persian Firdaria periods."""
        FIRDARIA_DIURNAL = ['sun', 'venus', 'mercury', 'moon', 'saturn',
                           'jupiter', 'mars']
        FIRDARIA_NOCTURNAL = ['moon', 'saturn', 'jupiter', 'mars', 'sun',
                             'venus', 'mercury']
        
        rulers = FIRDARIA_DIURNAL if is_diurnal else FIRDARIA_NOCTURNAL
        periods = []
        
        period_length = 75 / 7  # Each period is about 10 years, 8 months
        start_date = birth_date
        
        for i, planet in enumerate(rulers):
            period_start = start_date + timedelta(days=i * period_length * 365.25)
            period_end = start_date + timedelta(days=(i + 1) * period_length * 365.25)
            
            # Calculate subperiods
            subperiods = []
            subperiod_length = period_length / 7
            
            for j, subplanet in enumerate(rulers):
                sub_start = period_start + timedelta(days=j * subperiod_length * 365.25)
                sub_end = period_start + timedelta(days=(j + 1) * subperiod_length * 365.25)
                
                subperiods.append({
                    'planet': subplanet,
                    'start_date': sub_start,
                    'end_date': sub_end
                })
            
            periods.append({
                'planet': planet,
                'start_date': period_start,
                'end_date': period_end,
                'subperiods': subperiods
            })
        
        return periods
    
    def calculate_primary_directions(self, birth_chart: Dict,
                                  target_date: datetime,
                                  key_points: List[str] = None) -> List[Dict]:
        """Calculate primary directions using the Placidus method."""
        if not key_points:
            key_points = ['sun', 'moon', 'mercury', 'venus', 'mars',
                        'jupiter', 'saturn', 'ascendant', 'midheaven']
        
        directions = []
        
        # Calculate RAMC at birth
        ramc = self._calculate_ramc(birth_chart['angles']['midheaven'])
        
        # Calculate primary directions
        for significator in key_points:
            sig_pos = (birth_chart['planets'].get(significator) or 
                      birth_chart['angles'].get(significator))
            
            if not sig_pos:
                continue
                
            # Calculate significator's primary position
            sig_ra = self._ecliptic_to_ra(
                sig_pos['longitude'],
                sig_pos.get('latitude', 0)
            )
            
            # Find aspects to promissors
            for promissor in key_points:
                if promissor == significator:
                    continue
                    
                prom_pos = (birth_chart['planets'].get(promissor) or 
                           birth_chart['angles'].get(promissor))
                
                if not prom_pos:
                    continue
                    
                # Calculate promissor's position
                prom_ra = self._ecliptic_to_ra(
                    prom_pos['longitude'],
                    prom_pos.get('latitude', 0)
                )
                
                # Calculate arc
                arc = (prom_ra - sig_ra) % 360
                
                if arc > 180:
                    arc = 360 - arc
                    
                # A degree of RA equals approximately a year
                years = arc
                direction_date = birth_chart['timestamp'] + timedelta(days=years*365.25)
                
                if direction_date <= target_date:
                    directions.append({
                        'significator': significator,
                        'promissor': promissor,
                        'arc_degrees': arc,
                        'date': direction_date,
                        'completed': True
                    })
                else:
                    directions.append({
                        'significator': significator,
                        'promissor': promissor,
                        'arc_degrees': arc,
                        'date': direction_date,
                        'completed': False
                    })
        
        return sorted(directions, key=lambda x: x['date'])
    
    def _calculate_ramc(self, mc_longitude: float) -> float:
        """Calculate Right Ascension of Midheaven."""
        # This is a simplified calculation
        # For more precision, use the full formula considering obliquity
        return mc_longitude
    
    def _ecliptic_to_ra(self, longitude: float, latitude: float) -> float:
        """Convert ecliptic coordinates to right ascension."""
        # This is a simplified conversion
        # For more precision, use proper spherical trigonometry
        obliquity = 23.4367  # Mean obliquity of ecliptic
        
        # Convert to radians
        lon_rad = math.radians(longitude)
        lat_rad = math.radians(latitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate RA
        ra = math.atan2(
            math.sin(lon_rad) * math.cos(obl_rad) - 
            math.tan(lat_rad) * math.sin(obl_rad),
            math.cos(lon_rad)
        )
        
        # Convert back to degrees
        ra_deg = math.degrees(ra)
        if ra_deg < 0:
            ra_deg += 360
            
        return ra_deg
