# api/routes/status_routes/get.py

from fastapi import APIRouter
from api.services import status_services


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
