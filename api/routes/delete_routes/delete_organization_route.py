# api/routes/delete_routes/delete_organization_route.py

from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from api.config.ckan_settings import ckan_settings
from api.services import organization_services

router = APIRouter()


@router.delete(
    "/organization/{organization_name}",
    response_model=dict,
    summary="Delete an organization",
    description=(
        "Delete an organization from CKAN by its name, including "
        "all associated datasets and resources."
    ),
    responses={
        200: {
            "description": "Organization deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Organization deleted successfully"}
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error message explaining the bad request"}
                }
            },
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {"example": {"detail": "Organization not found"}}
            },
        },
    },
)
async def delete_organization(
    organization_name: str,
    server: Literal["local"] = Query(
        "local", description="Choose 'local'. Defaults to 'local'."
    ),
):
    """
    Endpoint to delete an organization in CKAN by its name.

    If ?server=pre_ckan is used, it will delete from the pre-CKAN instance
    if enabled. Returns a 400 error if pre_ckan is disabled or missing a
    valid scheme. Raises a 404 if the organization does not exist.
    """
    try:
        # Determine which CKAN instance to use
        if server == "pre_ckan":
            if not ckan_settings.pre_ckan_enabled:
                raise HTTPException(
                    status_code=400, detail="Pre-CKAN is disabled and cannot be used."
                )
            ckan_instance = ckan_settings.pre_ckan
        else:
            ckan_instance = ckan_settings.ckan

        organization_services.delete_organization(
            organization_name=organization_name, ckan_instance=ckan_instance
        )
        return {"message": "Organization deleted successfully"}

    except Exception as e:
        error_msg = str(e)
        if "Organization not found" in error_msg:
            raise HTTPException(status_code=404, detail="Organization not found")
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Pre-CKAN server is not configured or unreachable.",
            )
        raise HTTPException(status_code=400, detail=error_msg)
