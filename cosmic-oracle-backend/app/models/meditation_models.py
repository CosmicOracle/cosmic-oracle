# app/models/meditation_models.py
"""
Pydantic Models for the Meditation API.
"""
from pydantic import BaseModel, Field, conint, confloat
from typing import Optional, List, Literal
from datetime import date, datetime

MeditationType = Literal["mindfulness", "loving_kindness", "body_scan", "chakra_balancing"]

class RecordSessionRequest(BaseModel):
    """Defines the request for recording a new meditation session."""
    duration: conint(gt=0) = Field(..., example=20, description="Duration of the meditation in minutes.")
    meditation_type: MeditationType = Field(..., example="mindfulness")
    notes: Optional[str] = Field(None, max_length=1000)
    quality_rating: Optional[conint(ge=1, le=10)] = Field(None, example=8)

class OptimalTimeRequest(BaseModel):
    """Defines the request for finding optimal meditation times."""
    target_date_str: date = Field(..., example="2024-05-22")
    latitude: confloat(ge=-90, le=90) = Field(..., example=34.0522)
    longitude: confloat(ge=-180, le=180) = Field(..., example=-118.2437)
    timezone_str: str = Field(..., example="America/Los_Angeles")