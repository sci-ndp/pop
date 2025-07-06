# api/routes/tracking_routes/get_tracking_status.py

from fastapi import APIRouter

from api.config.keycloak_settings import keycloak_settings
from api.config.swagger_settings import swagger_settings
from api.config.tracking_settings import tracking_settings

router = APIRouter()


@router.get(
    "/tracking-status",
    summary="Get endpoint tracking configuration",
    description="Returns the current endpoint tracking configuration including client ID and organization.",
    responses={
        200: {
            "description": "Tracking configuration retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "tracking_enabled": True,
                        "client_id": "saleem_test",
                        "organization": "SCI - University of Utah",
                        "external_api_url": "https://api.example.com/endpoint-tracking",
                        "success_only": True,
                        "message": "Endpoint tracking is active and configured"
                    }
                }
            }
        }
    }
)
async def get_tracking_status():
    """
    Get the current endpoint tracking configuration.
    
    This endpoint demonstrates the tracking functionality and shows
    the configuration values that are being logged with each request.
    
    Returns:
        dict: Configuration information including client_id and organization
    """
    return {
        "tracking_enabled": tracking_settings.endpoint_tracking_enabled,
        "client_id": keycloak_settings.client_id,
        "organization": swagger_settings.organization,
        "external_api_url": tracking_settings.endpoint_tracking_api_url,
        "success_only": True,
        "request_data_tracking": True,
        "message": "Endpoint tracking is active and configured" if tracking_settings.endpoint_tracking_enabled else "Endpoint tracking is disabled"
    }
