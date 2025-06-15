"""
Routes for real astronomical calculations and data endpoints.
This module integrates with astronomical_service.py to provide accurate
astronomical data through a RESTful API.
"""
from fastapi import APIRouter
from app.api.endpoints import astronomical

# Create the router with a prefix and tags for Swagger documentation
astronomical_bp = APIRouter(
    prefix="/api/v1/astronomical",
    tags=["astronomical"]
)

# Include all routes from the astronomical endpoints
astronomical_bp.include_router(astronomical.router)

# Re-export the router for use in the main application
__all__ = ['astronomical_bp']
