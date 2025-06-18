# api/routes/search_routes/list_organizations_route.py
from typing import List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query

from api.config.ckan_settings import ckan_settings
from api.services import organization_services

router = APIRouter()


@router.get(
    "/organization",
    response_model=List[str],
    summary="List all organizations",
    description=(
        "Retrieve a list of all organizations, with optional name filtering "
        "and optional CKAN server selection."
    ),
    responses={
        200: {
            "description": "A list of all organizations",
            "content": {"application/json": {"example": ["org1", "org2", "org3"]}},
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error message explaining the bad request"}
                }
            },
        },
    },
)
async def list_organizations(
    name: Optional[str] = Query(
        None, description="An optional string to filter organizations by name"
    ),
    server: Literal["local", "global", "pre_ckan"] = Query(
        "global",
        description=(
            "Specify the server to list organizations from. Defaults to " "'local'."
        ),
    ),
):
    """
    Endpoint to list all organizations. Optionally, filter organizations
    by a partial name and specify the CKAN server.

    Parameters
    ----------
    name : Optional[str]
        A string to filter organizations by name (case-insensitive).
    server : Literal['local', 'global', 'pre_ckan']
        The CKAN server to list organizations from. Defaults to 'local'.

    Returns
    -------
    List[str]
        A list of organization names, optionally filtered by the provided
        name.

    Raises
    ------
    HTTPException
        If there is an error retrieving the list of organizations, an
        HTTPException is raised with a detailed message.
    """
    if server == "pre_ckan" and not ckan_settings.pre_ckan_enabled:
        raise HTTPException(
            status_code=400, detail="Pre-CKAN is disabled and cannot be used."
        )

    try:
        organizations = organization_services.list_organization(name, server)
        return organizations
    except Exception as e:
        # Convert the internal CKAN error to a more user-friendly message
        error_message = str(e)

        if "No scheme supplied" in error_message:
            # Provide a cleaner explanation for the user
            raise HTTPException(
                status_code=400,
                detail=("Server is not configured or " "is unreachable."),
            )

        # Otherwise, return the original error
        raise HTTPException(status_code=400, detail=error_message)
