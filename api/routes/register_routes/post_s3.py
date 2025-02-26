from fastapi import APIRouter, HTTPException, status, Depends
from api.services.s3_services.add_s3 import add_s3
from api.models.s3request_model import S3Request
from typing import Dict, Any
from api.services.keycloak_services.get_current_user import get_current_user
from api.config import ckan_settings  # Import the settings


router = APIRouter()


@router.post(
    "/s3",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new S3 resource",
    description="Create a new S3 resource.",
    responses={
        201: {
            "description": "Resource created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "12345678-abcd-efgh-ijkl-1234567890ab"
                    }
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
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add an S3 resource to CKAN.

    Parameters
    ----------
    data : S3Request
        An object containing all the required parameters for creating an
        S3 resource.

    Returns
    -------
    dict
        A dictionary containing the ID of the created resource if
        successful.

    Raises
    ------
    HTTPException
        If there is an error creating the resource, an HTTPException is
        raised with a detailed message.
    """
    try:
        # Determine which CKAN instance to use
        if ckan_settings.pre_ckan_enabled:
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
            ckan_instance=ckan_instance  # Pass the instance here
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
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
