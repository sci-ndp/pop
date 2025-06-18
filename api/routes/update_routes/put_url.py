# api/routes/update_routes/put_url.py

from typing import Any, Dict, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.config.ckan_settings import ckan_settings
from api.models.update_url_model import URLUpdateRequest
from api.services.keycloak_services.get_current_user import get_current_user
from api.services.url_services.update_url import update_url

router = APIRouter()


@router.put(
    "/url/{resource_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update an existing URL resource",
    description=(
        "Update an existing URL resource in CKAN.\n\n"
        "### Common Fields for All File Types\n"
        "- **resource_name**: The unique name of the resource.\n"
        "- **resource_title**: The title of the resource.\n"
        "- **owner_org**: The ID of the organization.\n"
        "- **resource_url**: The URL of the resource.\n"
        "- **file_type**: The file type (`stream`, `CSV`, `TXT`, `JSON`, "
        "`NetCDF`).\n"
        "- **notes**: Additional notes (optional).\n"
        "- **extras**: Additional metadata (optional).\n"
        "- **mapping**: Mapping information (optional).\n"
        "- **processing**: Processing info (optional).\n\n"
        "### Query Parameter\n"
        "Use `?server=local` or `?server=pre_ckan` to pick the CKAN instance. "
        "Defaults to 'local' if not provided.\n\n"
        "### Example Payload\n"
        "```\n"
        "{\n"
        '    "resource_name": "example_resource_name",\n'
        '    "resource_title": "Example Resource Title",\n'
        '    "owner_org": "example_org_id",\n'
        '    "resource_url": "http://example.com/resource",\n'
        '    "file_type": "CSV",\n'
        '    "notes": "Additional notes about the resource.",\n'
        '    "extras": {"key1": "value1", "key2": "value2"},\n'
        '    "mapping": {"field1": "mapping1", "field2": "mapping2"},\n'
        '    "processing": {\n'
        '        "delimiter": ",", "header_line": 1,\n'
        '        "start_line": 2, "comment_char": "#"\n'
        "    }\n"
        "}\n"
        "```\n"
    ),
    responses={
        200: {
            "description": "Resource updated successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Resource updated successfully"}
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error updating resource: <error>"}
                }
            },
        },
    },
)
async def update_url_resource(
    resource_id: str,
    data: URLUpdateRequest,
    server: Literal["local", "pre_ckan"] = Query(
        "local", description="Choose 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
    _: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update an existing URL resource in CKAN.

    If ?server=pre_ckan, uses the pre-CKAN instance if enabled. Otherwise,
    defaults to local CKAN. Returns a 400 error if pre_ckan is disabled
    or missing a valid scheme.
    """
    try:
        if server == "pre_ckan":
            if not ckan_settings.pre_ckan_enabled:
                raise HTTPException(
                    status_code=400, detail="Pre-CKAN is disabled and cannot be used."
                )
            ckan_instance = ckan_settings.pre_ckan
        else:
            ckan_instance = ckan_settings.ckan

        await update_url(
            resource_id=resource_id,
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
        return {"message": "Resource updated successfully"}

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
