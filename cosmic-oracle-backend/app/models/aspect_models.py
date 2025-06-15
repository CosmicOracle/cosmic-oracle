from pydantic import BaseModel, Field
from typing import List, Optional

class AspectCalculationPoint(BaseModel):
    """Input model for a single celestial point for aspect calculation."""
    name: str = Field(..., example="Sun")
    longitude: float = Field(..., example=123.45)
    speed_longitude: Optional[float] = Field(None, example=0.98)

class AspectCalculationRequest(BaseModel):
    """Request model for finding all aspects between a set of points."""
    points: List[AspectCalculationPoint]

class AspectDetail(BaseModel):
    """Output model for a single found aspect."""
    point1_name: str
    point2_name: str
    aspect_name: str
    aspect_type: str
    orb_degrees: float
    is_applying: Optional[bool]

class AspectCalculationResponse(BaseModel):
    aspects: List[AspectDetail]