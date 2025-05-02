from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, Literal
from api.services.s3_services.add_s3 import add_s3
from api.models.s3request_model import S3Request
from api.services.keycloak_services.get_current_user import get_current_user
from api.config import ckan_settings
from api.services.validation_services.validate_preckan_fields import (
    validate_preckan_fields,
)

router = APIRouter()


@router.post(
    "/s3",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new S3 resource",
    description=(
        "Create a new S3 resource.\n\n"
        "Use `?server=local` or `?server=pre_ckan` to choose the CKAN "
        "instance. Defaults to 'local' if not provided."
    ),
    responses={
        201: {
            "description": "Resource created successfully",
            "content": {
                "application/json": {
                    "example": {"id": "12345678-abcd-efgh-ijkl-1234567890ab"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error creating resource: <error message>"
                    }
                }
            }
        }
    }
)
async def create_s3_resource(
    data: S3Request,
    server: Literal["local", "pre_ckan"] = Query(
        "local",
        description="Specify 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add an S3 resource to CKAN.

    If server='pre_ckan', uses the pre-CKAN instance (if enabled). If
    the URL has no valid scheme, returns a friendly error. Otherwise,
    defaults to local CKAN.

    Parameters
    ----------
    data : S3Request
        Required parameters for creating an S3 resource.
    server : Literal['local', 'pre_ckan']
        Optional query param. Defaults to 'local'.
    _ : Dict[str, Any]
        User authentication details from Keycloak (unused).

    Returns
    -------
    dict
        A dictionary containing the ID of the created resource if successful.

    Raises
    ------
    HTTPException
        - 400: If there's an error creating the resource or invalid param.
    """
    try:
        if server == "pre_ckan":
            if not ckan_settings.pre_ckan_enabled:
                raise HTTPException(
                    status_code=400,
                    detail="Pre-CKAN is disabled and cannot be used."
                )

            document = data.dict()
            missing_fields = validate_preckan_fields(document)

            if missing_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required fields for pre_ckan: "
                           f"{missing_fields}"
                )

            ckan_instance = ckan_settings.pre_ckan
        else:
            ckan_instance = ckan_settings.ckan

        resource_id = add_s3(
            resource_name=data.resource_name,
            resource_title=data.resource_title,
            owner_org=data.owner_org,
            resource_s3=data.resource_s3,
            notes=data.notes,
            extras=data.extras,
            ckan_instance=ckan_instance
        )
        return {"id": resource_id}

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Reserved key error: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        error_msg = str(e)
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Pre-CKAN server is not configured or unreachable."
            )
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
