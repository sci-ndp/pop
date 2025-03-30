# api/routes/status_routes/get.py

from fastapi import APIRouter
from api.services import status_services
from api.services.status_services import get_full_metrics


router = APIRouter()


@router.get(
    "/",
    response_model=dict,
    summary="Check system status",
    description=(
        "Check if the CKAN and Keycloak servers are active "
        "andreachable.")
)
async def get_status():
    """
    Endpoint to check if CKAN and Keycloak are active and reachable.

    Returns
    -------
    str
        A message confirming if CKAN and Keycloak are active.

    Raises
    ------
    HTTPException
        If there is an error connecting to CKAN or Keycloak, an HTTPException
        is raised with a detailed message.
    """
    return_dict = status_services.get_status()

    return return_dict


@router.get(
    "/metrics",
    response_model=dict,
    summary="Retrieve system metrics",
    description="Returns detailed system metrics and service status."
)
async def get_metrics():
    """
    Endpoint to retrieve detailed system metrics.

    Returns
    -------
    dict
        System metrics (IP, CPU, memory, disk) and services status.
    """
    return get_full_metrics()
