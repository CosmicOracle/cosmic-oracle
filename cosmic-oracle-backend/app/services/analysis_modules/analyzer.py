# app/services/analysis_modules/analyzer.py
from typing import Dict, List, Any

class ChartAnalyzer:
    """Performs high-level analysis on chart distribution and balance."""
    
    ELEMENT_MAP = {'Aries': 'Fire', 'Taurus': 'Earth', 'Gemini': 'Air', 'Cancer': 'Water', 'Leo': 'Fire', 'Virgo': 'Earth', 'Libra': 'Air', 'Scorpio': 'Water', 'Sagittarius': 'Fire', 'Capricorn': 'Earth', 'Aquarius': 'Air', 'Pisces': 'Water'}
    MODALITY_MAP = {'Aries': 'Cardinal', 'Taurus': 'Fixed', 'Gemini': 'Mutable', 'Cancer': 'Cardinal', 'Leo': 'Fixed', 'Virgo': 'Mutable', 'Libra': 'Cardinal', 'Scorpio': 'Fixed', 'Sagittarius': 'Mutable', 'Capricorn': 'Cardinal', 'Aquarius': 'Fixed', 'Pisces': 'Mutable'}

    @staticmethod
    def analyze_distribution(points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates elemental, modality, and hemisphere balance."""
        elements = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
        modalities = {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}
        hemispheres = {'Northern': 0, 'Southern': 0, 'Eastern': 0, 'Western': 0}

        for point in points:
            sign = point.get('sign_name')
            house = point.get('house')
            if not sign: continue
            
            elements[ChartAnalyzer.ELEMENT_MAP[sign]] += 1
            modalities[ChartAnalyzer.MODALITY_MAP[sign]] += 1
            
            if house:
                if 1 <= house <= 6: hemispheres['Northern'] += 1
                if 7 <= house <= 12: hemispheres['Southern'] += 1
                if 1 <= house <= 3 or 10 <= house <= 12: hemispheres['Eastern'] += 1
                if 4 <= house <= 9: hemispheres['Western'] += 1
                
        return {
            "elemental_balance": elements,
            "modality_balance": modalities,
            "hemisphere_emphasis": hemispheres
        }

    @staticmethod
    def analyze_chart_shape(points: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Determines the chart shape based on Jones Patterns.
        This is a simplified implementation for demonstration.
        """
        longitudes = sorted([p['longitude'] for p in points])
        if not longitudes: return {"name": "Undefined", "description": "Not enough points to determine shape."}
        
        largest_gap = 0
        n = len(longitudes)
        for i in range(n):
            gap = (longitudes[(i + 1) % n] - longitudes[i] + 360) % 360
            if gap > largest_gap:
                largest_gap = gap
        
        span = 360 - largest_gap
        
        if span <= 120: return {"name": "Bundle", "description": "All planets are within a 120° arc. Specialist, focused energy."}
        if span <= 180:
             # Check for a "handle" to distinguish Bowl from Bucket
            for p_lon in longitudes:
                is_handle = True
                for other_lon in longitudes:
                    if p_lon == other_lon: continue
                    if (other_lon - p_lon + 360) % 360 > 180:
                        is_handle = False
                        break
                if is_handle:
                    return {"name": "Bucket", "description": "Most planets in a 180° arc with one opposite. Energy is directed via the 'handle' planet."}
            return {"name": "Bowl", "description": "All planets are within a 180° arc. Self-contained, subjective focus."}
        if largest_gap > 60 and largest_gap < 120: return {"name": "Locomotive", "description": "Planets occupy 240°. A driving, executive energy led by the 'engine' planet."}

        return {"name": "Splash", "description": "Planets are distributed widely. A versatile personality with diverse interests."}