# app/models/biorhythm_models.py
"""
Pydantic Models for the Biorhythm API.

These models define the data structures for API requests related to
biorhythm calculations, ensuring robust validation of dates and other parameters.
"""
from pydantic import BaseModel, Field, conint
from typing import Optional
from datetime import date

# Define a custom Pydantic type for date strings to use a built-in validator.
# This ensures dates are in the correct "YYYY-MM-DD" format.
ISODateString = date

class BiorhythmCurrentRequest(BaseModel):
    """
    Defines the request body for getting the current biorhythm values.
    """
    birth_date_str: ISODateString = Field(
        ...,
        example="1985-10-26",
        description="The user's birth date in YYYY-MM-DD format."
    )
    analysis_date_str: Optional[ISODateString] = Field(
        None,
        example="2024-05-21",
        description="The date to analyze. Defaults to the current date if not provided."
    )

class BiorhythmChartRequest(BaseModel):
    """
    Defines the request body for generating biorhythm chart data.
    """
    birth_date_str: ISODateString = Field(
        ...,
        example="1985-10-26",
        description="The user's birth date in YYYY-MM-DD format."
    )
    analysis_date_str: Optional[ISODateString] = Field(
        None,
        example="2024-05-21",
        description="The central date for the chart. Defaults to the current date if not provided."
    )
    days_before: conint(ge=1, le=90) = Field(
        15,
        description="Number of days to plot before the analysis date."
    )
    days_after: conint(ge=1, le=90) = Field(
        15,
        description="Number of days to plot after the analysis date."
    )