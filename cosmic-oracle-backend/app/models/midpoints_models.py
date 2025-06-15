# app/models/midpoints_models.py
"""
Pydantic Models for the Midpoints API.
"""
from pydantic import BaseModel, Field, condecimal, confloat
from typing import Optional

class MidpointsRequest(BaseModel):
    """Defines the request for calculating a midpoint tree."""
    datetime_str: str = Field(..., example="1971-06-28T09:44:00")
    timezone_str: str = Field(..., example="Africa/Johannesburg")
    latitude: condecimal(ge=-90, le=90) = Field(..., example=-26.2041)
    longitude: condecimal(ge=-180, le=180) = Field(..., example=28.0473)
    house_system: str = Field("Placidus", example="Placidus")
    aspect_orb: Optional[confloat(ge=0.1, le=3.0)] = Field(
        1.5, 
        description="The maximum orb in degrees for aspects to the midpoints (0.1 to 3.0)."
    )