# app/models/moon_models.py
"""
Pydantic Models for the Moon Service API.
"""
from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import date

ISODateString = date

class MoonPhaseRequest(BaseModel):
    """Defines the request for getting the Moon's phase. The datetime is optional."""
    datetime_utc_str: Optional[str] = Field(
        None,
        example="2024-05-21T18:00:00Z",
        description="Optional UTC datetime in ISO 8601 format. Defaults to now if not provided."
    )

class MoonRiseSetRequest(BaseModel):
    """Defines the request for getting Moon rise and set times."""
    target_date_str: ISODateString = Field(..., example="2024-05-21")
    latitude: condecimal(ge=-90, le=90) = Field(..., example=51.5074)
    longitude: condecimal(ge=-180, le=180) = Field(..., example=-0.1278)
    timezone_str: str = Field(..., example="Europe/London")