# api/routes/register_routes/post_general_dataset.py

from typing import Any, Dict, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.config import ckan_settings
from api.models.general_dataset_request_model import GeneralDatasetRequest
from api.services.dataset_services.general_dataset import create_general_dataset
from api.services.keycloak_services.get_current_user import get_current_user
from api.services.validation_services.validate_preckan_fields import (
    validate_preckan_fields,
)

router = APIRouter()


@router.post(
    "/dataset",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new general dataset",
    description=(
        "Create a new general dataset in CKAN with flexible schema.\n\n"
        "### Required Fields\n"
        "- **name**: Unique name for the dataset (lowercase, no spaces)\n"
        "- **title**: Human-readable title of the dataset\n"
        "- **owner_org**: Organization ID that owns this dataset\n\n"
        "### Optional Fields\n"
        "- **notes**: Description or notes about the dataset\n"
        "- **tags**: List of tags for categorizing the dataset\n"
        "- **extras**: Additional metadata as key-value pairs\n"
        "- **resources**: List of resources associated with this dataset\n"
        "- **private**: Whether the dataset is private (default: false)\n"
        "- **license_id**: License identifier for the dataset\n"
        "- **version**: Version of the dataset\n\n"
        "### Server Selection\n"
        "Use `?server=local` or `?server=pre_ckan` to choose the CKAN "
        "instance. Defaults to 'local' if not provided.\n\n"
        "### Example Payload\n"
        "```json\n"
        "{\n"
        '    "name": "my_research_dataset",\n'
        '    "title": "My Research Dataset",\n'
        '    "owner_org": "research_group",\n'
        '    "notes": "A comprehensive research dataset",\n'
        '    "tags": ["research", "climate"],\n'
        '    "extras": {\n'
        '        "project": "climate_study",\n'
        '        "version": "1.0"\n'
        "    },\n"
        '    "resources": [\n'
        "        {\n"
        '            "url": "http://example.com/data.csv",\n'
        '            "name": "main_data",\n'
        '            "format": "CSV",\n'
        '            "description": "Primary dataset"\n'
        "        }\n"
        "    ]\n"
        "}\n"
        "```\n"
    ),
    responses={
        201: {
            "description": "Dataset created successfully",
            "content": {
                "application/json": {
                    "example": {"id": "12345678-abcd-efgh-ijkl-1234567890ab"}
                }
            },
        },
        409: {
            "description": "Conflict - Duplicate dataset",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Duplicate Dataset",
                            "detail": ("A dataset with the given name already exists."),
                        }
                    }
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "server_error": {
                            "summary": "Server configuration error",
                            "value": {
                                "detail": ("Server is not configured or unreachable.")
                            },
                        },
                        "general_error": {
                            "summary": "General error",
                            "value": {"detail": "Error creating dataset: <error>"},
                        },
                    }
                }
            },
        },
    },
)
async def create_general_dataset_endpoint(
    data: GeneralDatasetRequest,
    server: Literal["local", "pre_ckan"] = Query(
        "local", description="Specify 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
    _: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a new general dataset in CKAN.

    This endpoint provides a flexible interface for creating datasets without
    being tied to specific resource types like S3, Kafka, or URL.

    Parameters
    ----------
    data : GeneralDatasetRequest
        Required/optional parameters for creating a general dataset.
    server : Literal['local', 'pre_ckan']
        If not provided, defaults to 'local'.
    _ : Dict[str, Any]
        Keycloak user auth (unused).

    Returns
    -------
    dict
        A dictionary containing the ID of the created dataset if successful.

    Raises
    ------
    HTTPException
        - 409: Duplicate dataset
        - 400: Invalid parameters, server configuration, or other errors
    """
    try:
        if server == "pre_ckan":
            if not ckan_settings.pre_ckan_enabled:
                raise HTTPException(
                    status_code=400, detail="Pre-CKAN is disabled and cannot be used."
                )

            document = data.dict()
            missing_fields = validate_preckan_fields(document)

            if missing_fields:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Missing required fields for pre_ckan: " f"{missing_fields}"
                    ),
                )

            ckan_instance = ckan_settings.pre_ckan
        else:
            ckan_instance = ckan_settings.ckan

        # Convert ResourceRequest objects to dictionaries
        resources = None
        if data.resources:
            resources = [resource.dict() for resource in data.resources]

        dataset_id = create_general_dataset(
            name=data.name,
            title=data.title,
            owner_org=data.owner_org,
            notes=data.notes,
            tags=data.tags,
            extras=data.extras,
            resources=resources,
            private=data.private,
            license_id=data.license_id,
            version=data.version,
            ckan_instance=ckan_instance,
        )
        return {"id": dataset_id}

    except ValueError as exc:
        # Handle validation errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except KeyError as exc:
        # Handle reserved key errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reserved key error: {str(exc)}",
        )
    except Exception as exc:
        error_msg = str(exc)

        # Handle specific error cases
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400, detail="Server is not configured or unreachable."
            )
        if (
            "That name is already in use" in error_msg
            or "That URL is already in use" in error_msg
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Duplicate Dataset",
                    "detail": "A dataset with the given name already exists.",
                },
            )

        # Generic error handling
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating dataset: {error_msg}",
        )
