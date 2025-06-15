# app/models/electional_models.py
"""
Pydantic Models for the Electional Astrology API.
"""
from pydantic import BaseModel, Field, conint, condecimal
from typing import Optional, List

class DesiredConditions(BaseModel):
    """A nested model to specify the desired astrological criteria."""
    desired_ascendant_signs: Optional[List[str]] = Field(
        None, 
        example=["Taurus", "Leo", "Sagittarius"],
        description="A list of acceptable signs for the Ascendant."
    )
    strengthen_planet: Optional[str] = Field(
        None,
        example="Jupiter",
        description="The key planet for the endeavor (e.g., 'Venus' for marriage, 'Jupiter' for business)."
    )
    avoid_malefics_on_angles: bool = Field(
        True,
        description="If true, penalize charts where Mars or Saturn are on the Asc, MC, Dsc, or IC."
    )

class ElectionalRequest(BaseModel):
    """Defines the request body for an electional astrology search."""
    start_datetime_str: str = Field(..., example="2024-01-01T00:00:00")
    end_datetime_str: str = Field(..., example="2024-01-07T23:59:59")
    timezone_str: str = Field(..., example="America/New_York")
    latitude: condecimal(ge=-90, le=90) = Field(..., example=40.7128)
    longitude: condecimal(ge=-180, le=180) = Field(..., example=-74.0060)
    desired_conditions: DesiredConditions