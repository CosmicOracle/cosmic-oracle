# app/services/compatibility_service.py
import logging
# Ensure all typing hints are imported
from typing import Dict, Any, List, Optional

# Import the necessary service classes (make sure these are the CLASS names)
from app.services.astrology_service import AstrologyService
from app.services.content_fetch_service import ContentFetchService

logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class CompatibilityService:
    _instance = None # Optional: For singleton pattern

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CompatibilityService, cls).__new__(cls)
        return cls._instance

    def __init__(self, astrology_service_instance: AstrologyService = None, content_fetch_service_instance: ContentFetchService = None):
        if hasattr(self, '_initialized') and self._initialized:
            return

        logger.info("Initializing CompatibilityService...")

        if astrology_service_instance is None:
            raise RuntimeError("AstrologyService instance must be provided to CompatibilityService.")
        self.astrology_service = astrology_service_instance

        if content_fetch_service_instance is None:
            raise RuntimeError("ContentFetchService instance must be provided to CompatibilityService.")
        self.content_fetch_service = content_fetch_service_instance

        # Load compatibility matrix (e.g., zodiac sign compatibility)
        self.compatibility_matrix = self.content_fetch_service.get_compatibility_matrix()
        if not self.compatibility_matrix:
            raise RuntimeError("Could not load compatibility matrix from content_fetch_service. Check compatibility_matrix.json.")

        self._initialized = True
        logger.info("CompatibilityService initialized successfully.")

    def get_relationship_report(self, person1_data: Dict[str, Any], person2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a comprehensive relationship compatibility report between two individuals.
        """
        logger.info(f"Generating compatibility report for {person1_data.get('full_name', 'Person 1')} and {person2_data.get('full_name', 'Person 2')}")

        try:
            # Step 1: Get natal charts for both individuals
            chart1 = self._get_person_chart(person1_data)
            chart2 = self._get_person_chart(person2_data)

            if "error" in chart1: return {"error": f"Person 1 chart error: {chart1['error']}"}
            if "error" in chart2: return {"error": f"Person 2 chart error: {chart2['error']}"}

            # Step 2: Calculate Zodiac Sign Compatibility (from content_fetch_service)
            p1_sun_sign_key = chart1['points']['Sun']['sign_key']
            p2_sun_sign_key = chart2['points']['Sun']['sign_key']
            zodiac_comp_rating = self._get_zodiac_compatibility(p1_sun_sign_key, p2_sun_sign_key)

            # Step 3: Calculate Inter-chart Aspects (Synastry)
            inter_chart_aspects = self._calculate_inter_chart_aspects(chart1, chart2)

            # Step 4: Simple interpretation based on aspects and zodiac
            synastry_summary = self._synthesize_synastry_summary(inter_chart_aspects, zodiac_comp_rating)

            return {
                "person1_chart_summary": {
                    "sun_sign": chart1['points']['Sun']['sign_name'],
                    "ascendant_sign": chart1['angles']['Ascendant']['sign_name']
                },
                "person2_chart_summary": {
                    "sun_sign": chart2['points']['Sun']['sign_name'],
                    "ascendant_sign": chart2['angles']['Ascendant']['sign_name']
                },
                "zodiac_sign_compatibility": {
                    "person1_sign": chart1['points']['Sun']['sign_name'],
                    "person2_sign": chart2['points']['Sun']['sign_name'],
                    "rating": zodiac_comp_rating
                },
                "synastry_analysis": {
                    "inter_chart_aspects": inter_chart_aspects,
                    "summary": synastry_summary
                },
                "full_report": "This is a detailed placeholder report. Real reports would integrate many more factors."
            }
        except Exception as e:
            logger.critical(f"Error generating compatibility report: {e}", exc_info=True)
            return {"error": "An unexpected error occurred during compatibility report generation."}

    def _get_person_chart(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to get a natal chart using AstrologyService."""
        required_fields = ["datetime_str", "timezone_str", "latitude", "longitude", "house_system"]
        missing_fields = [f for f in required_fields if f not in person_data]
        if missing_fields:
            raise ValueError(f"Missing required natal data fields: {', '.join(missing_fields)}")

        return self.astrology_service.get_natal_chart_details(
            datetime_str=person_data['datetime_str'],
            timezone_str=person_data['timezone_str'],
            latitude=person_data['latitude'],
            longitude=person_data['longitude'],
            house_system=person_data['house_system']
        )

    def _get_zodiac_compatibility(self, sign1_key: str, sign2_key: str) -> str:
        """Looks up compatibility rating from the loaded matrix."""
        matrix = self.compatibility_matrix
        if matrix and sign1_key in matrix and sign2_key in matrix[sign1_key]:
            return matrix[sign1_key][sign2_key]
        return "Unknown"

    def _calculate_inter_chart_aspects(self, chart1: Dict, chart2: Dict) -> List[Dict[str, Any]]:
        """
        Calculates aspects between planets/points in two different charts (Synastry).
        This is a simplified example; real synastry is complex.
        """
        aspects = []
        p1_points = {p['key']: p for p in list(chart1['points'].values()) + list(chart1['angles'].values())}
        p2_points = {p['key']: p for p in list(chart2['points'].values()) + list(chart2['angles'].values())}
        
        # Define some key points for synastry
        key_points = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "ascendant", "midheaven"]
        
        # Iterate over key points from chart1 and chart2
        for p1_key in key_points:
            p1 = p1_points.get(p1_key)
            if not p1: continue
            
            for p2_key in key_points:
                p2 = p2_points.get(p2_key)
                if not p2: continue

                # Avoid self-aspects if comparing same point
                if p1_key == p2_key: continue

                # Calculate separation (angle between them)
                separation = abs(p1['longitude'] - p2['longitude'])
                if separation > 180: separation = 360 - separation
                
                # Check for major aspects using aspects data from content_fetch_service
                aspect_base_data = self.content_fetch_service.get_aspect_base_data()
                if aspect_base_data: # Ensure data is loaded
                    for aspect_name, aspect_info in aspect_base_data.items():
                        aspect_angle = aspect_info.get('angle')
                        aspect_orb = aspect_info.get('orb', 5.0)
                        
                        if aspect_angle is not None and abs(separation - aspect_angle) <= aspect_orb:
                            aspects.append({
                                "person1_point": p1['name'],
                                "person2_point": p2['name'],
                                "aspect_name": aspect_name,
                                "orb_degrees": round(abs(separation - aspect_angle), 2),
                                "interpretation_snippet": f"({p1['name']} in {p1['sign_name']} aspecting {p2['name']} in {p2['sign_name']})"
                            })
        return aspects

    def _synthesize_synastry_summary(self, aspects: List[Dict[str, Any]], zodiac_comp_rating: str) -> str:
        """Generates a summary based on calculated synastry aspects and zodiac compatibility."""
        summary_parts = [f"Overall zodiac compatibility: {zodiac_comp_rating}."]
        
        if aspects:
            summary_parts.append("Key inter-chart aspects indicate:")
            for aspect in aspects[:3]: # Limit to top few for summary
                summary_parts.append(f"- {aspect['person1_point']} {aspect['aspect_name']} {aspect['person2_point']}.")
        else:
            summary_parts.append("No major inter-chart aspects found, suggesting a more neutral dynamic.")
            
        return " ".join(summary_parts)