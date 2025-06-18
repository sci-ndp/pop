# api/routes/register_routes/post_url.py

from typing import Any, Dict, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.config import ckan_settings
from api.models.urlrequest_model import URLRequest
from api.services.keycloak_services.get_current_user import get_current_user
from api.services.url_services.add_url import add_url

# from api.services.validation_services.validate_preckan_fields import (
#     validate_preckan_fields,
# )

router = APIRouter()


@router.post(
    "/url",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new URL resource",
    description=(
        "Create a new URL resource in CKAN.\n\n"
        "### Common Fields for All File Types\n"
        "- **resource_name**: The unique name of the resource.\n"
        "- **resource_title**: The title of the resource.\n"
        "- **owner_org**: The ID of the organization.\n"
        "- **resource_url**: The URL of the resource.\n"
        "- **file_type**: The file type (`stream`, `CSV`, `TXT`, `JSON`, "
        "`NetCDF`).\n"
        "- **notes**: Additional notes (optional).\n"
        "- **extras**: Additional metadata (optional).\n"
        "- **mapping**: Mapping info (optional).\n"
        "- **processing**: Processing info (optional).\n\n"
        "### Selecting the Server\n"
        "Use `?server=local` or `?server=pre_ckan` to pick the CKAN instance. "
        "Defaults to 'local' if not provided.\n"
    ),
    responses={
        201: {
            "description": "Resource created successfully",
            "content": {
                "application/json": {
                    "example": {"id": "12345678-abcd-efgh-ijkl-1234567890ab"}
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error creating resource: <error message>"}
                }
            },
        },
    },
)
async def create_url_resource(
    data: URLRequest,
    server: Literal["local", "pre_ckan"] = Query(
        "local", description="Choose 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
    _: Dict[str, Any] = Depends(get_current_user),
):
    """
    Add a URL resource to CKAN.

    If server='pre_ckan', uses the pre-CKAN instance if enabled. Otherwise,
    defaults to local CKAN. A 400 error is returned if pre_ckan is disabled
    or the URL has no valid scheme.

    Parameters
    ----------
    data : URLRequest
        Required fields for creating a URL resource.
    server : Literal['local', 'pre_ckan']
        Optional query param. Defaults to 'local'.
    _ : Dict[str, Any]
        Keycloak user auth details (unused).

    Returns
    -------
    dict
        A dictionary containing the ID of the created resource if successful.

    Raises
    ------
    HTTPException
        - 400: If there's an error creating the resource, or if pre_ckan
          is disabled, or if there's no valid scheme.
    """
    try:
        if server == "pre_ckan":
            if not ckan_settings.pre_ckan_enabled:
                raise HTTPException(
                    status_code=400, detail="Pre-CKAN is disabled and cannot be used."
                )
            # Validate required fields for pre_ckan insertion
            # document = data.dict()
            # missing_fields = validate_preckan_fields(document)

            # if missing_fields:
            #     raise HTTPException(
            #         status_code=400,
            #         detail=("Missing required fields for "
            #                 f"pre_ckan: {missing_fields}")
            #     )

            ckan_instance = ckan_settings.pre_ckan
        else:
            ckan_instance = ckan_settings.ckan

        resource_id = add_url(
            resource_name=data.resource_name,
            resource_title=data.resource_title,
            owner_org=data.owner_org,
            resource_url=data.resource_url,
            file_type=data.file_type,
            notes=data.notes,
            extras=data.extras,
            mapping=data.mapping,
            processing=data.processing,
            ckan_instance=ckan_instance,
        )
        return {"id": resource_id}

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Reserved key error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Pre-CKAN server is not configured or unreachable.",
            )
        raise HTTPException(status_code=400, detail=error_msg)
