# app/services/dignities_service.py
"""
Advanced Astrological Dignities Service

This service calculates all traditional essential and accidental dignities,
providing precise evaluation of planetary strength and condition.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import math

from app.services.astronomical_service import AstronomicalService

logger = logging.getLogger(__name__)

class DignitiesService:
    """Service for calculating traditional astrological dignities."""
    
    # Essential Dignity Tables
    RULERSHIPS = {
        'aries': 'mars',
        'taurus': 'venus',
        'gemini': 'mercury',
        'cancer': 'moon',
        'leo': 'sun',
        'virgo': 'mercury',
        'libra': 'venus',
        'scorpio': 'mars',
        'sagittarius': 'jupiter',
        'capricorn': 'saturn',
        'aquarius': 'saturn',
        'pisces': 'jupiter'
    }
    
    EXALTATIONS = {
        'sun': {'sign': 'aries', 'degree': 19},
        'moon': {'sign': 'taurus', 'degree': 3},
        'mercury': {'sign': 'virgo', 'degree': 15},
        'venus': {'sign': 'pisces', 'degree': 27},
        'mars': {'sign': 'capricorn', 'degree': 28},
        'jupiter': {'sign': 'cancer', 'degree': 15},
        'saturn': {'sign': 'libra', 'degree': 21}
    }
    
    # Triplicities (by day)
    TRIPLICITIES = {
        'fire': ['sun', 'jupiter', 'saturn'],
        'earth': ['venus', 'moon', 'mars'],
        'air': ['saturn', 'mercury', 'jupiter'],
        'water': ['venus', 'mars', 'moon']
    }
    
    # Egyptian terms
    TERMS = {
        'aries': [
            {'planet': 'jupiter', 'end_degree': 6},
            {'planet': 'venus', 'end_degree': 12},
            {'planet': 'mercury', 'end_degree': 20},
            {'planet': 'mars', 'end_degree': 25},
            {'planet': 'saturn', 'end_degree': 30}
        ],
        # ... (terms for other signs)
    }
    
    def __init__(self, astronomical_service: AstronomicalService):
        self.astronomical = astronomical_service
    
    def calculate_essential_dignities(self, planet: str,
                                    sign: str,
                                    degree: float) -> Dict[str, Any]:
        """Calculate all essential dignities for a planet."""
        dignities = {
            'ruler': self._check_rulership(planet, sign),
            'exaltation': self._check_exaltation(planet, sign, degree),
            'triplicity': self._check_triplicity(planet, sign),
            'term': self._check_term(planet, sign, degree),
            'face': self._check_face(planet, sign, degree),
            'detriment': self._check_detriment(planet, sign),
            'fall': self._check_fall(planet, sign, degree)
        }
        
        # Calculate dignity scores
        scores = {
            'ruler': 5 if dignities['ruler'] else 0,
            'exaltation': 4 if dignities['exaltation'] else 0,
            'triplicity': 3 if dignities['triplicity'] else 0,
            'term': 2 if dignities['term'] else 0,
            'face': 1 if dignities['face'] else 0,
            'detriment': -5 if dignities['detriment'] else 0,
            'fall': -4 if dignities['fall'] else 0
        }
        
        total_score = sum(scores.values())
        
        return {
            'dignities': dignities,
            'scores': scores,
            'total_score': total_score,
            'condition': self._evaluate_condition(total_score)
        }
    
    def calculate_accidental_dignities(self, planet_data: Dict,
                                     chart_data: Dict) -> Dict[str, Any]:
        """Calculate accidental dignities (circumstantial strength)."""
        accidental_dignities = {
            'angular': self._is_angular(planet_data['house']),
            'direct': planet_data['speed'] > 0,
            'swift': abs(planet_data['speed']) > self._get_mean_speed(planet_data['name']),
            'oriental': self._is_oriental(planet_data, chart_data),
            'cazimi': self._is_cazimi(planet_data, chart_data),
            'combustion': self._is_combust(planet_data, chart_data),
            'under_sunbeams': self._is_under_sunbeams(planet_data, chart_data),
            'joy': self._is_in_joy(planet_data),
            'hayz': self._is_in_hayz(planet_data, chart_data),
            'mutual_reception': self._check_mutual_reception(planet_data, chart_data)
        }
        
        # Calculate accidental dignity scores
        scores = {
            'angular': 5 if accidental_dignities['angular'] else 0,
            'direct': 4 if accidental_dignities['direct'] else -4,
            'swift': 2 if accidental_dignities['swift'] else 0,
            'oriental': 2 if accidental_dignities['oriental'] else 0,
            'cazimi': 5 if accidental_dignities['cazimi'] else 0,
            'combustion': -6 if accidental_dignities['combustion'] else 0,
            'under_sunbeams': -2 if accidental_dignities['under_sunbeams'] else 0,
            'joy': 3 if accidental_dignities['joy'] else 0,
            'hayz': 5 if accidental_dignities['hayz'] else 0,
            'mutual_reception': 5 if accidental_dignities['mutual_reception'] else 0
        }
        
        total_score = sum(scores.values())
        
        return {
            'accidental_dignities': accidental_dignities,
            'scores': scores,
            'total_score': total_score,
            'condition': self._evaluate_condition(total_score)
        }
    
    def _check_rulership(self, planet: str, sign: str) -> bool:
        """Check if planet rules the sign."""
        return self.RULERSHIPS[sign.lower()] == planet.lower()
    
    def _check_exaltation(self, planet: str, sign: str, degree: float) -> bool:
        """Check if planet is exalted."""
        exalt = self.EXALTATIONS.get(planet.lower())
        if not exalt:
            return False
        
        return (exalt['sign'] == sign.lower() and
                abs(degree - exalt['degree']) <= 1)
    
    def _check_triplicity(self, planet: str, sign: str) -> bool:
        """Check if planet is in its triplicity."""
        element = self._get_element(sign)
        return planet.lower() in self.TRIPLICITIES[element]
    
    def _check_term(self, planet: str, sign: str, degree: float) -> bool:
        """Check if planet is in its own term."""
        terms = self.TERMS.get(sign.lower(), [])
        for term in terms:
            if (term['planet'] == planet.lower() and
                degree <= term['end_degree']):
                return True
        return False
    
    def _check_face(self, planet: str, sign: str, degree: float) -> bool:
        """Check if planet is in its face (decan)."""
        decan = int(degree / 10) + 1
        # Implementation depends on which face system you're using
        # This is a simplified version
        return False
    
    def _check_detriment(self, planet: str, sign: str) -> bool:
        """Check if planet is in detriment."""
        opposite_sign = self._get_opposite_sign(sign)
        return self.RULERSHIPS[opposite_sign] == planet.lower()
    
    def _check_fall(self, planet: str, sign: str, degree: float) -> bool:
        """Check if planet is in fall."""
        exalt = self.EXALTATIONS.get(planet.lower())
        if not exalt:
            return False
            
        opposite_sign = self._get_opposite_sign(exalt['sign'])
        return (sign.lower() == opposite_sign and
                abs(degree - exalt['degree']) <= 1)
    
    def _get_element(self, sign: str) -> str:
        """Get element of a sign."""
        elements = {
            'aries': 'fire', 'leo': 'fire', 'sagittarius': 'fire',
            'taurus': 'earth', 'virgo': 'earth', 'capricorn': 'earth',
            'gemini': 'air', 'libra': 'air', 'aquarius': 'air',
            'cancer': 'water', 'scorpio': 'water', 'pisces': 'water'
        }
        return elements[sign.lower()]
    
    def _get_opposite_sign(self, sign: str) -> str:
        """Get opposite sign."""
        opposites = {
            'aries': 'libra', 'taurus': 'scorpio',
            'gemini': 'sagittarius', 'cancer': 'capricorn',
            'leo': 'aquarius', 'virgo': 'pisces',
            'libra': 'aries', 'scorpio': 'taurus',
            'sagittarius': 'gemini', 'capricorn': 'cancer',
            'aquarius': 'leo', 'pisces': 'virgo'
        }
        return opposites[sign.lower()]
    
    def _evaluate_condition(self, score: float) -> str:
        """Evaluate planetary condition based on score."""
        if score >= 8:
            return 'excellently dignified'
        elif score >= 5:
            return 'well dignified'
        elif score >= 2:
            return 'moderately dignified'
        elif score >= -1:
            return 'neutral'
        elif score >= -4:
            return 'somewhat debilitated'
        elif score >= -7:
            return 'significantly debilitated'
        else:
            return 'severely debilitated'
    
    def _is_angular(self, house: int) -> bool:
        """Check if planet is in an angular house."""
        return house in [1, 4, 7, 10]
    
    def _get_mean_speed(self, planet: str) -> float:
        """Get mean daily motion of a planet."""
        mean_speeds = {
            'moon': 13.2,
            'mercury': 1.0,
            'venus': 1.0,
            'sun': 1.0,
            'mars': 0.5,
            'jupiter': 0.083,
            'saturn': 0.034
        }
        return mean_speeds.get(planet.lower(), 0)
    
    def _is_oriental(self, planet_data: Dict, chart_data: Dict) -> bool:
        """Check if planet is oriental to the Sun."""
        if planet_data['name'].lower() in ['sun', 'moon']:
            return False
            
        sun_lon = chart_data['planets']['sun']['longitude']
        planet_lon = planet_data['longitude']
        
        # Calculate shortest distance
        diff = planet_lon - sun_lon
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
            
        return diff > 0
    
    def _is_cazimi(self, planet_data: Dict, chart_data: Dict) -> bool:
        """Check if planet is cazimi (in heart of Sun)."""
        if planet_data['name'].lower() == 'sun':
            return False
            
        sun_lon = chart_data['planets']['sun']['longitude']
        planet_lon = planet_data['longitude']
        
        return abs(planet_lon - sun_lon) <= 0.25  # Within 17 minutes
    
    def _is_combust(self, planet_data: Dict, chart_data: Dict) -> bool:
        """Check if planet is combust."""
        if planet_data['name'].lower() == 'sun':
            return False
            
        sun_lon = chart_data['planets']['sun']['longitude']
        planet_lon = planet_data['longitude']
        
        separation = abs(planet_lon - sun_lon)
        if separation > 180:
            separation = 360 - separation
            
        return separation <= 8.5  # Within 8.5 degrees
    
    def _is_under_sunbeams(self, planet_data: Dict, chart_data: Dict) -> bool:
        """Check if planet is under the Sun's beams."""
        if planet_data['name'].lower() == 'sun':
            return False
            
        sun_lon = chart_data['planets']['sun']['longitude']
        planet_lon = planet_data['longitude']
        
        separation = abs(planet_lon - sun_lon)
        if separation > 180:
            separation = 360 - separation
            
        return separation <= 17  # Within 17 degrees
    
    def _is_in_joy(self, planet_data: Dict) -> bool:
        """Check if planet is in its house of joy."""
        joys = {
            'mercury': 1,  # 1st house
            'moon': 3,     # 3rd house
            'venus': 5,    # 5th house
            'mars': 6,     # 6th house
            'sun': 9,      # 9th house
            'jupiter': 11, # 11th house
            'saturn': 12   # 12th house
        }
        return planet_data['house'] == joys.get(planet_data['name'].lower())
    
    def _is_in_hayz(self, planet_data: Dict, chart_data: Dict) -> bool:
        """Check if planet is in hayz."""
        # A planet is in hayz if:
        # 1. It's diurnal and in a diurnal sign above horizon during day, or
        # 2. It's nocturnal and in a nocturnal sign below horizon during night
        sun_pos = chart_data['planets']['sun']
        is_daytime = sun_pos['house'] in range(7, 13)  # Sun above horizon
        
        planet_name = planet_data['name'].lower()
        if planet_name in ['sun', 'jupiter', 'saturn']:  # Diurnal planets
            return (is_daytime and
                    self._is_in_diurnal_sign(planet_data['sign']) and
                    planet_data['house'] in range(7, 13))
        elif planet_name in ['moon', 'venus', 'mars']:  # Nocturnal planets
            return (not is_daytime and
                    not self._is_in_diurnal_sign(planet_data['sign']) and
                    planet_data['house'] in range(1, 7))
        return False
    
    def _is_in_diurnal_sign(self, sign: str) -> bool:
        """Check if sign is diurnal."""
        return sign.lower() in ['aries', 'gemini', 'leo',
                              'libra', 'sagittarius', 'aquarius']
    
    def _check_mutual_reception(self, planet_data: Dict,
                              chart_data: Dict) -> bool:
        """Check for mutual reception by rulership."""
        planet = planet_data['name'].lower()
        sign = planet_data['sign'].lower()
        
        # Get the ruler of the sign the planet is in
        sign_ruler = self.RULERSHIPS[sign]
        
        # Get the sign that ruler is in
        ruler_data = chart_data['planets'].get(sign_ruler)
        if not ruler_data:
            return False
            
        ruler_sign = ruler_data['sign'].lower()
        
        # Check if the original planet rules the sign its ruler is in
        return self.RULERSHIPS[ruler_sign] == planet
