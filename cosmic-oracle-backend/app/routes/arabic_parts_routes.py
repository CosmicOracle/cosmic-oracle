# app/routes/arabic_parts_routes.py (or whichever file contains this router)

from fastapi import APIRouter, HTTPException, status, Depends # <-- Added Depends
from ..models.birth_data import NatalDataRequest
from ..models.arabic_parts_models import ArabicPartsResponse
# Import the singleton instance directly
from ..services.arabic_parts_service import arabic_parts_service_instance
from ..core.dependencies import get_api_key # <-- Added this import

router = APIRouter(
    prefix="/arabic-parts",
    tags=["Advanced Astrology"],
    dependencies=[Depends(get_api_key)] # <-- Added this line to apply API key protection
)

@router.post("/", response_model=ArabicPartsResponse)
async def get_arabic_parts_calculation(natal_data: NatalDataRequest):
    """
    Calculates all Arabic Parts (Lots) for a given natal chart.
    This endpoint now requires a valid API key.
    """
    if arabic_parts_service_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Arabic Parts service is not available."
        )

    result = arabic_parts_service_instance.calculate_all_parts(natal_data.dict())

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result