from pydantic import BaseModel, Field
from typing import Dict, Any, Literal
from .birth_data import NatalDataRequest # Reuse our natal data model

# --- Models for Dashboard Summary ---
class DashboardSummaryResponse(BaseModel):
    title: str
    summary_text: str
    dynamic_tip: str
    source_data_loaded: bool
    ai_powered: bool

# --- Models for Astrological Interpretation ---
class InterpretationRequest(BaseModel):
    # Allow any dictionary for chart_data for flexibility
    chart_data: Dict[str, Any] = Field(..., example={"planets": {"Sun": "15 Aries"}, "aspects": ["Sun square Moon"]})
    interpretation_type: Literal["general", "transit", "compatibility"] = Field(..., example="general")

class InterpretationResponse(BaseModel):
    interpretation: str
    type: str
    generated_at: str
    ai_powered: bool
    confidence: str