from fastapi import APIRouter, Depends, HTTPException, status
from ..services.aspect_service import aspect_service_instance
from ..models.aspect_models import AspectCalculationRequest, AspectCalculationResponse
from ..core.dependencies import get_api_key # Import your security guard

router = APIRouter(
    prefix="/aspects",
    tags=["Core Astrology"],
    dependencies=[Depends(get_api_key)] # Secure all endpoints in this file
)

@router.post("/calculate", response_model=AspectCalculationResponse)
async def find_all_aspects(request: AspectCalculationRequest):
    """
    Calculates all astrological aspects for a given list of celestial points.
    """
    if aspect_service_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Aspect service is not available."
        )

    # The service expects a list of dictionaries, so we convert our Pydantic models
    points_as_dicts = [p.dict() for p in request.points]

    found_aspects = aspect_service_instance.find_all_aspects(points_as_dicts)

    return {"aspects": found_aspects}
