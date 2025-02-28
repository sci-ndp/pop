# api/routes/search_routes/list_organizations_route.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Literal
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
            "content": {
                "application/json": {
                    "example": ["org1", "org2", "org3"]
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error message explaining the bad request"
                    }
                }
            }
        }
    }
)
async def list_organizations(
    name: Optional[str] = Query(
        None,
        description="An optional string to filter organizations by name"
    ),
    server: Literal["local", "global", "pre_ckan"] = Query(
        "local",
        description=(
            "Specify the server to list organizations from. Defaults to "
            "'local'."
        )
    )
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
    try:
        organizations = organization_services.list_organization(name, server)
        return organizations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
