# api/routes/register_routes/post_service.py
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, Literal
from api.services.service_services.add_service import add_service
from api.models.service_request_model import ServiceRequest
from api.services.keycloak_services.get_current_user import get_current_user
from api.config import ckan_settings
from api.services.validation_services.validate_preckan_fields import (
    validate_preckan_fields,
)

router = APIRouter()


@router.post(
    "/services",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new service",
    description=(
        "Register a new service and its associated metadata to the system.\n\n"
        "### Required Fields\n"
        "- **service_name**: The unique name of the service to be created.\n"
        "- **service_title**: The title of the service to be created.\n"
        "- **owner_org**: Must be 'services' (organization for all services).\n"
        "- **service_url**: The URL where the service is accessible.\n\n"
        "### Optional Fields\n"
        "- **service_type**: Type of service (API, Web Service, etc.).\n"
        "- **notes**: A description of the service.\n"
        "- **extras**: Additional metadata as CKAN extras.\n"
        "- **health_check_url**: URL for service health check endpoint.\n"
        "- **documentation_url**: URL to service documentation.\n\n"
        "### Selecting the Server\n"
        "Pass `?server=local` or `?server=pre_ckan` in the query string.\n"
        "If not provided, defaults to 'local'.\n\n"
        "### Example Payload\n"
        "{\n"
        '    \"service_name\": \"user_auth_api\",\n'
        '    \"service_title\": \"User Authentication API\",\n'
        '    \"owner_org\": \"services\",\n'
        '    \"service_url\": \"https://api.example.com/auth\",\n'
        '    \"service_type\": \"API\",\n'
        '    \"notes\": \"RESTful API for user authentication\",\n'
        '    \"extras\": {\n'
        '        \"version\": \"2.1.0\",\n'
        '        \"environment\": \"production\"\n'
        '    },\n'
        '    \"health_check_url\": \"https://api.example.com/auth/health\",\n'
        '    \"documentation_url\": \"https://docs.example.com/auth-api\"\n'
        "}\n"
    ),
    responses={
        201: {
            "description": "Service registered successfully",
            "content": {
                "application/json": {
                    "example": {"id": "12345678-abcd-efgh-ijkl-1234567890ab"}
                }
            }
        },
        409: {
            "description": "Conflict - Duplicate service",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Duplicate Service",
                            "detail": (
                                "A service with the given name or URL "
                                "already exists."
                            )
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_organization": {
                            "summary": "Invalid organization",
                            "value": {
                                "detail": (
                                    "owner_org must be 'services' for "
                                    "service registration"
                                )
                            }
                        },
                        "server_error": {
                            "summary": "Server configuration error",
                            "value": {
                                "detail": (
                                    "Server is not configured or unreachable."
                                )
                            }
                        },
                        "general_error": {
                            "summary": "General error",
                            "value": {
                                "detail": "Error creating service: <error>"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def create_service(
    data: ServiceRequest,
    server: Literal["local", "pre_ckan"] = Query(
        "local",
        description="Specify 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Register a new service and its associated metadata to the system.

    All services are registered under the 'services' organization.
    This endpoint creates both a CKAN dataset and resource for the service.

    Parameters
    ----------
    data : ServiceRequest
        Required/optional parameters for creating a service.
    server : Literal['local', 'pre_ckan']
        If not provided, defaults to 'local'.
    _ : Dict[str, Any]
        Keycloak user auth (unused).

    Returns
    -------
    dict
        A dictionary containing the ID of the created service if successful.

    Raises
    ------
    HTTPException
        - 409: Duplicate service
        - 400: Invalid parameters, server configuration, or other errors
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

        service_id = add_service(
            service_name=data.service_name,
            service_title=data.service_title,
            owner_org=data.owner_org,
            service_url=data.service_url,
            service_type=data.service_type,
            notes=data.notes,
            extras=data.extras,
            health_check_url=data.health_check_url,
            documentation_url=data.documentation_url,
            ckan_instance=ckan_instance
        )
        return {"id": service_id}

    except ValueError as exc:
        # Handle validation errors (e.g., wrong owner_org)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except KeyError as exc:
        # Handle reserved key errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reserved key error: {str(exc)}"
        )
    except Exception as exc:
        error_msg = str(exc)
        
        # Handle specific error cases
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Server is not configured or unreachable."
            )
        if ("That URL is already in use" in error_msg
                or "That name is already in use" in error_msg):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Duplicate Service",
                    "detail": (
                        "A service with the given name or URL "
                        "already exists."
                    )
                }
            )
        
        # Generic error handling
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating service: {error_msg}"
        )
