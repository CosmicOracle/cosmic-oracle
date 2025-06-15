# app/routes/antiscia_routes.py (or whichever file contains this router)

from fastapi import APIRouter, HTTPException, status, Depends # <-- Added Depends
from ..models.birth_data import NatalDataRequest
from ..models.antiscia_models import AntisciaResponse
from ..services.antiscia_service import calculate_antiscia_and_contra_antiscia
from ..core.dependencies import get_api_key # <-- Added this import

router = APIRouter(
    prefix="/antiscia",
    tags=["Advanced Astrology"],
    dependencies=[Depends(get_api_key)] # <-- Added this line to apply API key protection
)

@router.post("/", response_model=AntisciaResponse)
async def get_antiscia_calculation(natal_data: NatalDataRequest):
    """
    Calculates the antiscia and contra-antiscia points for a given natal chart.
    This endpoint now requires a valid API key.
    """
    result = calculate_antiscia_and_contra_antiscia(natal_data.dict())

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result