from fastapi import APIRouter, Depends, HTTPException, status # Keep status for potential future use or consistency
from ..services.ai_synthesis_service import AISynthesisService
from ..core.dependencies import get_ai_synthesis_service, get_api_key # IMPORTANT: Make sure get_api_key is imported
from ..models.birth_data import NatalDataRequest
from ..models.ai_models import DashboardSummaryResponse, InterpretationRequest, InterpretationResponse

router = APIRouter(
    prefix="/ai",
    tags=["AI Synthesis"],
    dependencies=[Depends(get_api_key)] # <-- This line applies the API key dependency to all routes in this router
)

@router.post("/dashboard-summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    user_data: NatalDataRequest,
    ai_service: AISynthesisService = Depends(get_ai_synthesis_service)
):
    """
    Generates a personalized AI-powered dashboard summary.
    This endpoint now requires a valid API key due to the router-level dependency.
    """
    summary = ai_service.generate_dashboard_summary(user_data.dict())
    return summary

@router.post("/interpretation", response_model=InterpretationResponse)
async def get_astrological_interpretation(
    request: InterpretationRequest,
    ai_service: AISynthesisService = Depends(get_ai_synthesis_service)
):
    """
    Generates a detailed astrological interpretation using AI.
    This endpoint now requires a valid API key due to the router-level dependency.
    """
    interpretation = ai_service.generate_astrological_interpretation(
        chart_data=request.chart_data,
        interpretation_type=request.interpretation_type
    )
    return interpretation