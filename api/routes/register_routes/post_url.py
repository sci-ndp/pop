# api/routes/register_routes/post_url.py
from fastapi import APIRouter, HTTPException, status, Depends
from api.services.url_services.add_url import add_url
from api.models.urlrequest_model import URLRequest
from typing import Dict, Any
from api.services.keycloak_services.get_current_user import get_current_user
from api.config import ckan_settings  # Import the CKAN settings


router = APIRouter()


@router.post(
    "/url",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new URL resource",
    description=(
        "Create a new URL resource in CKAN.\n\n"
        "### Common Fields for All File Types\n"
        "- **resource_name**: The unique name of the resource to be created.\n"
        "- **resource_title**: The title of the resource to be created.\n"
        "- **owner_org**: The ID of the organization to which the resource "
        "belongs.\n"
        "- **resource_url**: The URL of the resource to be added.\n"
        "- **file_type**: The type of the file (`stream`, `CSV`, `TXT`, "
        "`JSON`, `NetCDF`).\n"
        "- **notes**: Additional notes about the resource (optional).\n"
        "- **extras**: Additional metadata to be added to the resource "
        "package as extras (optional).\n"
        "- **mapping**: Mapping information for the dataset (optional).\n"
        "- **processing**: Processing information for the "
        "dataset (optional).\n"
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
async def create_url_resource(
    data: URLRequest,
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add a URL resource to CKAN.

    Parameters
    ----------
    data : URLRequest
        An object containing all the required parameters for creating a
        URL resource.

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
        # Choose the CKAN instance based on pre_ckan_enabled
        if ckan_settings.pre_ckan_enabled:
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
            ckan_instance=ckan_instance  # Pass the CKAN instance
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
