# api/routes/update_routes/put_s3.py

from typing import Any, Dict, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.config.ckan_settings import ckan_settings
from api.models.update_s3_model import S3ResourceUpdateRequest
from api.services.keycloak_services.get_current_user import get_current_user
from api.services.s3_services.update_s3 import update_s3

router = APIRouter()


@router.put(
    "/s3/{resource_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update an existing S3 resource",
    description=(
        "Update an existing S3 resource and its associated metadata.\n\n"
        "### Optional Fields\n"
        "- **resource_name**: The unique name of the resource.\n"
        "- **resource_title**: The title of the resource.\n"
        "- **owner_org**: The ID of the organization.\n"
        "- **resource_s3**: The S3 URL of the resource.\n"
        "- **notes**: Additional notes.\n"
        "- **extras**: Additional metadata.\n\n"
        "### Query Parameter\n"
        "Use `?server=local` or `?server=pre_ckan` to choose which CKAN "
        "instance to update. Defaults to 'local' if not provided.\n\n"
        "### Example Payload\n"
        "```json\n"
        "{\n"
        '    "resource_name": "updated_resource_name",\n'
        '    "resource_s3": "http://new-s3-url.com/resource"\n'
        "}\n"
        "```\n"
    ),
    responses={
        200: {
            "description": "S3 resource updated successfully",
            "content": {
                "application/json": {
                    "example": {"message": "S3 resource updated successfully"}
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": ("Error updating S3 resource: <error message>")
                    }
                }
            },
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {"example": {"detail": "S3 resource not found"}}
            },
        },
    },
)
async def update_s3_resource(
    resource_id: str,
    data: S3ResourceUpdateRequest,
    server: Literal["local", "pre_ckan"] = Query(
        "local", description="Choose 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
    _: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update an existing S3 resource in CKAN.

    If ?server=pre_ckan is used and pre_ckan is enabled/configured,
    updates the resource in the pre-CKAN instance. Otherwise defaults
    to local CKAN. Returns a 400 error if pre_ckan is disabled or
    missing a valid scheme.
    """
    try:
        # Determine CKAN instance
        if server == "pre_ckan":
            if not ckan_settings.pre_ckan_enabled:
                raise HTTPException(
                    status_code=400, detail="Pre-CKAN is disabled and cannot be used."
                )
            ckan_instance = ckan_settings.pre_ckan
        else:
            ckan_instance = ckan_settings.ckan

        updated_id = await update_s3(
            resource_id=resource_id,
            resource_name=data.resource_name,
            resource_title=data.resource_title,
            owner_org=data.owner_org,
            resource_s3=data.resource_s3,
            notes=data.notes,
            extras=data.extras,
            ckan_instance=ckan_instance,
        )
        if not updated_id:
            raise HTTPException(status_code=404, detail="S3 resource not found")
        return {"message": "S3 resource updated successfully"}

    except Exception as exc:
        error_msg = str(exc)
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Pre-CKAN server is not configured or unreachable.",
            )
        raise HTTPException(status_code=400, detail=error_msg)
