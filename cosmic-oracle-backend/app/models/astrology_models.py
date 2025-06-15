# cosmic-oracle-backend/app/models/astrology_models.py
from pydantic import BaseModel, Field

class NatalChartInput(BaseModel):
    """
    Defines the validated input structure for a natal chart request.
    This model is used by both the Swiss Ephemeris and Skyfield endpoints.
    """
    datetime_str: str = Field(
        ...,
        description="The full birth date and time in ISO 8601 format.",
        example="1990-01-15T16:45:00"
    )
    timezone_str: str = Field(
        ...,
        description="IANA timezone name (e.g., 'America/New_York', 'Europe/London').",
        example="America/Los_Angeles"
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Geographical latitude of the birth location (-90.0 to 90.0).",
        example=34.0522
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Geographical longitude of the birth location (-180.0 to 180.0).",
        example=-118.2437
    )
    altitude: float = Field(
        0.0,
        description="Altitude in meters above sea level. Used by Swiss Ephemeris engine.",
        example=71
    )
    house_system: str = Field(
        "Placidus",
        description="The house system to use. Primarily used by the Swiss Ephemeris engine.",
        example="Placidus"
    )