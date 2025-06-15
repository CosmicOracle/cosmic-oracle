# app/services/pattern_service.py
"""
Advanced Astrological Pattern Detection Service

This service analyzes charts for complex patterns including:
- Aspect patterns (Grand Trines, T-Squares, etc.)
- Harmonic patterns and resonances
- Planetary patterns and distributions
- Midpoint structures and symmetries
"""
import logging
from typing import Dict, Any, List, Optional
import math
from dataclasses import dataclass

from app.services.astronomical_service import AstronomicalService
from app.services.aspect_service import AspectService

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """Represents an astrological pattern in a chart."""
    type: str
    planets: List[str]
    aspects: List[Dict[str, Any]]
    quality: str  # Element or mode
    orb: float
    power: float  # Pattern strength/significance

class PatternService:
    """Service for detecting and analyzing astrological patterns."""
    
    def __init__(self, astronomical_service: AstronomicalService,
                 aspect_service: AspectService):
        self.astronomical = astronomical_service
        self.aspect_service = aspect_service
    
    def find_all_patterns(self, chart: Dict[str, Any],
                         max_orb: float = 8.0) -> Dict[str, List[Pattern]]:
        """Find all major aspect patterns in a chart."""
        patterns = {
            'grand_trines': self.find_grand_trines(chart, max_orb),
            'grand_crosses': self.find_grand_crosses(chart, max_orb),
            't_squares': self.find_t_squares(chart, max_orb),
            'yods': self.find_yods(chart, max_orb),
            'mystic_rectangles': self.find_mystic_rectangles(chart, max_orb),
            'kites': self.find_kites(chart, max_orb),
            'thors_hammers': self.find_thors_hammers(chart, max_orb),
            'grand_sextiles': self.find_grand_sextiles(chart, max_orb)
        }
        
        return patterns
    
    def find_grand_trines(self, chart: Dict[str, Any],
                         max_orb: float = 8.0) -> List[Pattern]:
        """Find all grand trines in the chart."""
        grand_trines = []
        planets = list(chart['planets'].items())
        
        for i in range(len(planets) - 2):
            for j in range(i + 1, len(planets) - 1):
                for k in range(j + 1, len(planets)):
                    p1_name, p1_data = planets[i]
                    p2_name, p2_data = planets[j]
                    p3_name, p3_data = planets[k]
                    
                    # Check for three trines
                    trine1 = self._check_aspect(p1_data, p2_data, 120, max_orb)
                    trine2 = self._check_aspect(p2_data, p3_data, 120, max_orb)
                    trine3 = self._check_aspect(p3_data, p1_data, 120, max_orb)
                    
                    if trine1 and trine2 and trine3:
                        # Determine element
                        element = self._get_element(p1_data['sign'])
                        if (self._get_element(p2_data['sign']) == element and
                            self._get_element(p3_data['sign']) == element):
                            
                            # Calculate average orb
                            avg_orb = (trine1['orb'] + trine2['orb'] + trine3['orb']) / 3
                            
                            grand_trines.append(Pattern(
                                type='grand_trine',
                                planets=[p1_name, p2_name, p3_name],
                                aspects=[trine1, trine2, trine3],
                                quality=element,
                                orb=avg_orb,
                                power=self._calculate_pattern_power(
                                    'grand_trine',
                                    [p1_data, p2_data, p3_data],
                                    avg_orb
                                )
                            ))
        
        return sorted(grand_trines, key=lambda x: x.orb)
    
    def find_grand_crosses(self, chart: Dict[str, Any],
                          max_orb: float = 8.0) -> List[Pattern]:
        """Find all grand crosses in the chart."""
        grand_crosses = []
        planets = list(chart['planets'].items())
        
        for i in range(len(planets) - 3):
            for j in range(i + 1, len(planets) - 2):
                for k in range(j + 1, len(planets) - 1):
                    for l in range(k + 1, len(planets)):
                        p1_name, p1_data = planets[i]
                        p2_name, p2_data = planets[j]
                        p3_name, p3_data = planets[k]
                        p4_name, p4_data = planets[l]
                        
                        # Check for four squares and two oppositions
                        square1 = self._check_aspect(p1_data, p2_data, 90, max_orb)
                        square2 = self._check_aspect(p2_data, p3_data, 90, max_orb)
                        square3 = self._check_aspect(p3_data, p4_data, 90, max_orb)
                        square4 = self._check_aspect(p4_data, p1_data, 90, max_orb)
                        opp1 = self._check_aspect(p1_data, p3_data, 180, max_orb)
                        opp2 = self._check_aspect(p2_data, p4_data, 180, max_orb)
                        
                        if all([square1, square2, square3, square4, opp1, opp2]):
                            # Determine modality
                            mode = self._get_modality(p1_data['sign'])
                            if (self._get_modality(p2_data['sign']) == mode and
                                self._get_modality(p3_data['sign']) == mode and
                                self._get_modality(p4_data['sign']) == mode):
                                
                                avg_orb = (square1['orb'] + square2['orb'] +
                                         square3['orb'] + square4['orb'] +
                                         opp1['orb'] + opp2['orb']) / 6
                                
                                grand_crosses.append(Pattern(
                                    type='grand_cross',
                                    planets=[p1_name, p2_name, p3_name, p4_name],
                                    aspects=[square1, square2, square3, square4,
                                           opp1, opp2],
                                    quality=mode,
                                    orb=avg_orb,
                                    power=self._calculate_pattern_power(
                                        'grand_cross',
                                        [p1_data, p2_data, p3_data, p4_data],
                                        avg_orb
                                    )
                                ))
        
        return sorted(grand_crosses, key=lambda x: x.orb)
    
    def find_yods(self, chart: Dict[str, Any],
                  max_orb: float = 8.0) -> List[Pattern]:
        """Find all yod configurations (Finger of God)."""
        yods = []
        planets = list(chart['planets'].items())
        
        for i in range(len(planets) - 2):
            for j in range(i + 1, len(planets) - 1):
                for k in range(j + 1, len(planets)):
                    p1_name, p1_data = planets[i]
                    p2_name, p2_data = planets[j]
                    p3_name, p3_data = planets[k]
                    
                    # Check for two quincunxes and one sextile
                    quincunx1 = self._check_aspect(p1_data, p3_data, 150, max_orb)
                    quincunx2 = self._check_aspect(p2_data, p3_data, 150, max_orb)
                    sextile = self._check_aspect(p1_data, p2_data, 60, max_orb)
                    
                    if quincunx1 and quincunx2 and sextile:
                        avg_orb = (quincunx1['orb'] + quincunx2['orb'] +
                                 sextile['orb']) / 3
                        
                        yods.append(Pattern(
                            type='yod',
                            planets=[p1_name, p2_name, p3_name],
                            aspects=[quincunx1, quincunx2, sextile],
                            quality='mutable',  # Yods are generally mutable
                            orb=avg_orb,
                            power=self._calculate_pattern_power(
                                'yod',
                                [p1_data, p2_data, p3_data],
                                avg_orb
                            )
                        ))
        
        return sorted(yods, key=lambda x: x.orb)
    
    def _check_aspect(self, planet1: Dict, planet2: Dict,
                     aspect_degree: float, max_orb: float) -> Optional[Dict]:
        """Check if two planets form a specific aspect."""
        diff = abs(planet1['longitude'] - planet2['longitude'])
        if diff > 180:
            diff = 360 - diff
            
        orb = abs(diff - aspect_degree)
        if orb <= max_orb:
            return {
                'aspect_type': self._get_aspect_type(aspect_degree),
                'degree': aspect_degree,
                'orb': orb,
                'applying': self._is_aspect_applying(
                    planet1['speed'],
                    planet2['speed'],
                    planet1['longitude'],
                    planet2['longitude'],
                    aspect_degree
                )
            }
        return None
    
    def _get_element(self, sign: str) -> str:
        """Get element of a sign."""
        elements = {
            'aries': 'fire', 'leo': 'fire', 'sagittarius': 'fire',
            'taurus': 'earth', 'virgo': 'earth', 'capricorn': 'earth',
            'gemini': 'air', 'libra': 'air', 'aquarius': 'air',
            'cancer': 'water', 'scorpio': 'water', 'pisces': 'water'
        }
        return elements[sign.lower()]
    
    def _get_modality(self, sign: str) -> str:
        """Get modality of a sign."""
        modalities = {
            'aries': 'cardinal', 'cancer': 'cardinal',
            'libra': 'cardinal', 'capricorn': 'cardinal',
            'taurus': 'fixed', 'leo': 'fixed',
            'scorpio': 'fixed', 'aquarius': 'fixed',
            'gemini': 'mutable', 'virgo': 'mutable',
            'sagittarius': 'mutable', 'pisces': 'mutable'
        }
        return modalities[sign.lower()]
    
    def _get_aspect_type(self, degree: float) -> str:
        """Get aspect type from degree."""
        aspects = {
            0: 'conjunction',
            60: 'sextile',
            90: 'square',
            120: 'trine',
            150: 'quincunx',
            180: 'opposition'
        }
        return aspects.get(degree, 'unknown')
    
    def _is_aspect_applying(self, speed1: float, speed2: float,
                          lon1: float, lon2: float,
                          aspect_degree: float) -> bool:
        """Determine if aspect is applying or separating."""
        relative_speed = speed1 - speed2
        
        # Calculate current angular separation
        diff = lon1 - lon2
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
        return abs(diff - target_diff) > abs(diff + relative_speed - target_diff)
    
    def _calculate_pattern_power(self, pattern_type: str,
                               planet_data: List[Dict],
                               orb: float) -> float:
        """Calculate the strength/significance of a pattern."""
        # Base power by pattern type
        base_powers = {
            'grand_trine': 8,
            'grand_cross': 10,
            'yod': 7,
            'mystic_rectangle': 6,
            'kite': 9,
            'thors_hammer': 7,
            'grand_sextile': 12
        }
        
        base = base_powers.get(pattern_type, 5)
        
        # Adjust for planet dignities and speeds
        planet_factor = sum(1 for p in planet_data if abs(p['speed']) > 1) / len(planet_data)
        
        # Adjust for orb precision
        orb_factor = 1 - (orb / 10)  # 10° is max orb
        
        # Calculate final power
        power = base * planet_factor * orb_factor
        
        return round(power, 2)

    def calculate_harmonic_patterns(self, chart: Dict[str, Any],
                                  harmonic: int) -> Dict[str, Any]:
        """Calculate harmonic patterns and resonances."""
        harmonic_positions = {}
        
        # Calculate harmonic positions
        for planet, data in chart['planets'].items():
            # Multiply longitude by harmonic number and reduce
            harm_lon = (data['longitude'] * harmonic) % 360
            harmonic_positions[planet] = harm_lon
        
        # Find conjunctions in harmonic chart
        conjunctions = []
        planets = list(harmonic_positions.items())
        
        for i in range(len(planets) - 1):
            for j in range(i + 1, len(planets)):
                p1_name, p1_lon = planets[i]
                p2_name, p2_lon = planets[j]
                
                diff = abs(p1_lon - p2_lon)
                if diff > 180:
                    diff = 360 - diff
                    
                if diff <= 10:  # Use 10° orb for harmonics
                    conjunctions.append({
                        'planets': [p1_name, p2_name],
                        'degrees': [p1_lon, p2_lon],
                        'orb': diff
                    })
        
        return {
            'harmonic': harmonic,
            'positions': harmonic_positions,
            'conjunctions': conjunctions,
            'resonance_score': self._calculate_harmonic_resonance(
                conjunctions, len(chart['planets'])
            )
        }
    
    def _calculate_harmonic_resonance(self, conjunctions: List[Dict],
                                    total_planets: int) -> float:
        """Calculate the strength of harmonic resonance."""
        if not conjunctions:
            return 0.0
            
        # Count unique planets involved
        unique_planets = set()
        for conj in conjunctions:
            unique_planets.update(conj['planets'])
            
        # Calculate resonance
        involvement = len(unique_planets) / total_planets
        precision = 1 - (sum(c['orb'] for c in conjunctions) /
                        (len(conjunctions) * 10))
        
        return round(involvement * precision * 10, 2)  # Scale to 0-10
