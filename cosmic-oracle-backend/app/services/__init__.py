# app/services/__init__.py

# This file exports all the main service classes from the
# individual service modules within the `app/services` directory.

# Core Services
from .astrology_service import AstrologyService
from .skyfield_service import SkyfieldService # Ensure this is SkyfieldService CLASS
from .horoscope_service import HoroscopeService
from .numerology_service import NumerologyService # <-- Now correctly importing the CLASS
from .moon_service import MoonService
from .compatibility_service import CompatibilityService

# Other General Services
from .ai_synthesis_service import AISynthesisService
from .auth_service import AuthService
from .content_fetch_service import ContentFetchService
from .report_generation_service import ReportGenerationService
from .user_service import UserService
from .zodiac_service import ZodiacService

# Astrological Calculation & Specific Feature Services (ensure all are classes)
from .antiscia_service import AntisciaService
from .arabic_parts_service import ArabicPartsService
from .aspect_service import AspectService
from .astral_calendar_service import AstralCalendarService
from .astrology_engine import AstrologyEngine
from .biorhythm_service import BiorhythmService
from .birth_chart_service import BirthChartService
from .chakra_service import ChakraService
from .composite_service import CompositeService
from .crystal_service import CrystalService
from .declination_service import DeclinationService
from .electional_service import ElectionalService
from .fixed_star_service import FixedStarService
from .heliacal_service import HeliacalService
from .horary_service import HoraryService
from .house_calculator_service import HouseCalculatorService
from .immanuel_service import ImmanuelService
from .lunar_mansion_service import LunarMansionService
from .mathematical_points_service import MathematicalPointsService
from .meditation_service import MeditationService
from .midpoints_service import MidpointsService
from .monitoring_service import MonitoringService
from .personal_forecast_service import PersonalForecastService
from .personal_sky_service import PersonalSkyService
from .planetary_hours_service import PlanetaryHoursService
from .predictive_service import PredictiveService
from .ritual_service import RitualService
from .solar_return_service import SolarReturnService
from .star_catalog_service import StarCatalogService
from .subscription_service import SubscriptionService
from .synastry_service import SynastryService
from .tarot_service import TarotService
from .transit_forecasting_service import TransitForecastingService
from .year_ahead_report_service import YearAheadReportService

# Define __all__ for explicit exports (optional, but good practice for clarity)
__all__ = [
    # Core Services
    'AstrologyService',
    'SkyfieldService',
    'HoroscopeService',
    'NumerologyService', # <-- Now correctly listed as the class
    'MoonService',
    'CompatibilityService',

    # Other General Services
    'AISynthesisService',
    'AuthService',
    'ContentFetchService',
    'ReportGenerationService',
    'UserService',
    'ZodiacService',

    # Astrological Calculation & Specific Feature Services
    'AntisciaService',
    'ArabicPartsService',
    'AspectService',
    'AstralCalendarService',
    'AstrologyEngine',
    'BiorhythmService',
    'BirthChartService',
    'ChakraService',
    'CompositeService',
    'CrystalService',
    'DeclinationService',
    'ElectionalService',
    'FixedStarService',
    'HeliacalService',
    'HoraryService',
    'HouseCalculatorService',
    'ImmanuelService',
    'LunarMansionService',
    'MathematicalPointsService',
    'MeditationService',
    'MidpointsService',
    'MonitoringService',
    'PersonalForecastService',
    'PersonalSkyService',
    'PlanetaryHoursService',
    'PredictiveService',
    'RitualService',
    'SolarReturnService',
    'StarCatalogService',
    'SubscriptionService',
    'SynastryService',
    'TarotService',
    'TransitForecastingService',
    'YearAheadReportService',
]