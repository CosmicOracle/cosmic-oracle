# app/services/mathematical_points_service.py
"""
Service for calculating advanced mathematical and sensitive points in an astrological chart.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# --- REUSE: Import the primary astrology service ---
from app.services.astrology_service import get_natal_chart_details, AstrologyEngine
from app.services.content_fetch_service import get_mathematical_points_content
from app.services.moon_service import moon_service_instance # For Syzygy calculation

logger = logging.getLogger(__name__)

class MathematicalPointsService:
    """
    A singleton service that calculates various mathematical points like the
    Vertex, Equatorial Ascendant, and Pre-Natal Syzygy.
    """
    _instance = None

    def __init__(self):
        logger.info("Initializing MathematicalPointsService singleton...")
        self.interpretations = get_mathematical_points_content().get("interpretations", {})
        if not self.interpretations:
            raise RuntimeError("Could not load necessary mathematical points content file.")
        logger.info("MathematicalPointsService initialized successfully.")

    def _calculate_pre_natal_syzygy(self, birth_dt_utc: datetime) -> Dict[str, Any]:
        """
        Calculates the longitude and type of the New or Full Moon immediately preceding birth.
        This uses a more robust search method than the original.
        """
        # Search backward from the birth time for up to 30 days.
        end_t = moon_service_instance.ts.from_datetime(birth_dt_utc)
        start_t = moon_service_instance.ts.from_datetime(birth_dt_utc - timedelta(days=30))
        
        # Use Skyfield's phase finder
        t, y = moon_service_instance.phases(moon_service_instance.eph, start_t, end_t)
        
        if len(t) == 0:
            return {"error": "Could not find a pre-natal syzygy within 30 days of birth."}

        # The last event found in the list is the one immediately preceding birth.
        last_event_time = t[-1]
        last_event_phase_code = y[-1]

        phase_name = "New Moon" if last_event_phase_code == 0 else "Full Moon"
        
        # Get the longitude of the Sun/Moon at that exact moment.
        syzygy_point = moon_service_instance.eph['sun'].at(last_event_time)
        _, lon, _ = syzygy_point.frame_latlon(ecliptic_frame)

        return {
            "name": "Pre-Natal Syzygy",
            "type": phase_name,
            "datetime_utc": last_event_time.utc_iso(),
            "longitude": lon.degrees
        }

    def calculate_all_points(self, natal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public facade to generate a full report of all calculated mathematical points.
        """
        logger.info("Calculating mathematical points.")
        try:
            # Step 1: Generate the base natal chart to get raw data.
            chart = get_natal_chart_details(**natal_data)
            if 'error' in chart:
                return {"error": f"Could not calculate base natal chart: {chart['error']}"}

            # Step 2: Use a temporary AstrologyEngine instance to access its internal methods.
            birth_dt_utc = datetime.fromisoformat(chart['chart_info']['datetime_utc'])
            engine = AstrologyEngine(
                dt_utc=birth_dt_utc,
                latitude=chart['chart_info']['latitude'],
                longitude=chart['chart_info']['longitude'],
                altitude=0,
                house_system=natal_data['house_system']
            )
            
            # Step 3: Calculate each point.
            # Vertex is already calculated as part of a full chart's angles.
            vertex_data = chart.get('angles', {}).get('Vertex', {})
            vertex_lon = vertex_data.get('longitude')
            
            # Equatorial Ascendant
            _, ascmc_ex = swe.houses_ex(engine.julian_day_utc, engine.latitude, engine.longitude, b'E')
            eq_asc_lon = ascmc_ex[4]

            # Pre-Natal Syzygy
            syzygy_data = self._calculate_pre_natal_syzygy(birth_dt_utc)

            # Step 4: Assemble and format the final report with interpretations.
            points_report = []

            if vertex_lon is not None:
                formatted_vertex = engine._format_point("Vertex", vertex_lon)
                formatted_vertex['interpretation'] = self.interpretations.get("Vertex", {})
                points_report.append(formatted_vertex)

            if eq_asc_lon is not None:
                formatted_eq_asc = engine._format_point("Equatorial Ascendant", eq_asc_lon)
                formatted_eq_asc['interpretation'] = self.interpretations.get("Equatorial Ascendant", {})
                points_report.append(formatted_eq_asc)
            
            if "error" not in syzygy_data:
                formatted_syzygy = engine._format_point(syzygy_data['name'], syzygy_data['longitude'])
                formatted_syzygy['interpretation'] = self.interpretations.get("Pre-Natal Syzygy", {})
                formatted_syzygy['type'] = syzygy_data['type'] # Add the phase type
                points_report.append(formatted_syzygy)

            # Part of Fortune is already included in a full chart calculation.
            pof_data = chart.get('part_of_fortune', {})
            if 'error' not in pof_data:
                pof_data['interpretation'] = self.interpretations.get("Part of Fortune", {})
                points_report.append(pof_data)
            
            return {
                "mathematical_points_report": points_report,
                "natal_chart_used": chart['chart_info']
            }

        except Exception as e:
            logger.critical(f"An unexpected fatal error in the mathematical points service: {e}", exc_info=True)
            return {"error": "An unexpected internal server error occurred during calculation."}

# --- Create a single, shared instance ---
try:
    mathematical_points_service_instance = MathematicalPointsService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate MathematicalPointsService: {e}")
    mathematical_points_service_instance = None