# app/models/monitoring_models.py
"""
Pydantic Models for the Subscription Monitoring API.
"""
from pydantic import BaseModel, Field, conint
from typing import Optional

class MetricsRequest(BaseModel):
    """Defines the optional query parameters for the metrics endpoint."""
    days: conint(ge=1, le=365) = Field(30, description="The number of past days to include in the metrics calculation (1-365).")