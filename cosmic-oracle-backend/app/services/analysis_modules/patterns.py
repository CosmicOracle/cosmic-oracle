# app/services/analysis_modules/patterns.py
from typing import Dict, List, Any, Tuple
from itertools import combinations

class PatternDetector:
    """Detects major astrological chart patterns like T-Squares and Grand Trines."""

    @staticmethod
    def find_patterns(points: List[Dict[str, Any]], aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        
        # Efficiently group aspects by type
        oppositions = [a for a in aspects if a['aspect_name'] == 'opposition']
        squares = [a for a in aspects if a['aspect_name'] == 'square']
        trines = [a for a in aspects if a['aspect_name'] == 'trine']
        sextiles = [a for a in aspects if a['aspect_name'] == 'sextile']
        quincunxes = [a for a in aspects if a['aspect_name'] == 'quincunx']
        
        patterns.extend(PatternDetector._find_t_squares(oppositions, squares))
        patterns.extend(PatternDetector._find_grand_trines(points, trines))
        patterns.extend(PatternDetector._find_yods(sextiles, quincunxes))
        
        return patterns

    @staticmethod
    def _find_t_squares(oppositions: List[Dict], squares: List[Dict]) -> List[Dict]:
        t_squares = []
        for opp in oppositions:
            p1, p2 = opp['point1_key'], opp['point2_key']
            for sq in squares:
                focal_point = None
                if sq['point1_key'] == p1 and sq['point2_key'] not in [p1, p2]: focal_point = sq['point2_key']
                elif sq['point2_key'] == p1 and sq['point1_key'] not in [p1, p2]: focal_point = sq['point1_key']
                
                if focal_point:
                    # Now check if focal_point also squares p2
                    for other_sq in squares:
                        if (focal_point in [other_sq['point1_key'], other_sq['point2_key']] and
                            p2 in [other_sq['point1_key'], other_sq['point2_key']]):
                            
                            t_squares.append({
                                "pattern_name": "T-Square",
                                "involved_points": sorted(list(set([opp['point1_name'], opp['point2_name'], sq.get('point1_name'), sq.get('point2_name')]))),
                                "focal_point": points_map[focal_point]['name'], # requires a point key->name map
                                "description": "Dynamic tension and conflict requiring resolution through the focal point."
                            })
                            break # Found the t-square, move to next opposition
        return t_squares # Note: This needs a point_map for focal_point name, passed from main engine

    @staticmethod
    def _find_grand_trines(points: List[Dict], trines: List[Dict]) -> List[Dict]:
        grand_trines = []
        point_map = {p['key']: p for p in points}
        
        # Group points by element
        elements = {'Fire': [], 'Earth': [], 'Air': [], 'Water': []}
        for p in points:
            sign_name = p.get('sign_name')
            if sign_name:
                element = ChartAnalyzer.ELEMENT_MAP[sign_name]
                elements[element].append(p['key'])
                
        for element, p_keys in elements.items():
            if len(p_keys) >= 3:
                for combo in combinations(p_keys, 3):
                    p1, p2, p3 = combo
                    # Check for trines between all three pairs
                    if (PatternDetector._is_aspected(p1, p2, trines) and
                        PatternDetector._is_aspected(p1, p3, trines) and
                        PatternDetector._is_aspected(p2, p3, trines)):
                        grand_trines.append({
                            "pattern_name": f"Grand Trine ({element})",
                            "involved_points": [point_map[k]['name'] for k in combo],
                            "focal_point": None,
                            "description": "Natural talent, harmony, and ease. A self-contained circuit of energy."
                        })
        return grand_trines

    # ... (Yod detection would be similar, checking sextiles and quincunxes)
    # This structure is now easily extensible for more patterns.

    @staticmethod
    def _is_aspected(p1_key: str, p2_key: str, aspects: List[Dict]) -> bool:
        """Helper to check if two points have a specific aspect between them."""
        for a in aspects:
            if (p1_key == a['point1_key'] and p2_key == a['point2_key']) or \
               (p1_key == a['point2_key'] and p2_key == a['point1_key']):
                return True
        return False

# You would also create files for fixed_stars, midpoints, etc. in a similar fashion.