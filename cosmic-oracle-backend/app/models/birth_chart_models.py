# app/models/birth_chart_models.py
"""
Pydantic Models for the Birth Chart API.
"""
from pydantic import BaseModel, Field, condecimal

class BirthChartRequest(BaseModel):
    """Defines the request body for creating or updating a birth chart."""
    # Fixed: 'example' moved to 'json_schema_extra'
    datetime_str: str = Field(
        ...,
        json_schema_extra={'example': "1990-01-15T16:45:00"}
    )
    
    # Fixed: 'example' moved to 'json_schema_extra'
    timezone_str: str = Field(
        ...,
        json_schema_extra={'example': "America/Los_Angeles"}
    )
    
    # Fixed: 'example' moved to 'json_schema_extra'
    birth_location: str = Field(
        ...,
        max_length=150,
        json_schema_extra={'example': "Los Angeles, CA, USA"}
    )
    
    # Fixed: 'example' moved to 'json_schema_extra'
    latitude: condecimal(ge=-90, le=90) = Field(
        ...,
        json_schema_extra={'example': 34.0522}
    )
    
    # Fixed: 'example' moved to 'json_schema_extra'
    longitude: condecimal(ge=-180, le=180) = Field(
        ...,
        json_schema_extra={'example': -118.2437}
    )