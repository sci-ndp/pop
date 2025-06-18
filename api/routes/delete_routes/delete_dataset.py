# api/routes/delete_routes/resource_delete_route.py
# English code comments, PEP-8 lines <=79 chars

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query

from api.config.ckan_settings import ckan_settings
from api.services import dataset_services

router = APIRouter()


@router.delete(
    "/resource",
    response_model=dict,
    summary="Delete a resource by id",
    description="Delete a resource by its id.",
    responses={
        200: {
            "description": "Resource deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Resource deleted successfully"}
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
                "application/json": {"example": {"detail": "Resource not found"}}
            },
        },
    },
)
async def delete_resource(
    resource_id: Annotated[str, Query(description="The ID of the dataset to delete.")],
    server: Literal["local", "pre_ckan"] = Query(
        "local", description="Choose 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
):
    """
    Endpoint to delete a dataset by its resource_id.

    If ?server=pre_ckan is provided and pre_ckan is enabled, deletes from
    the pre-CKAN instance. Otherwise defaults to local CKAN.
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

        dataset_services.delete_dataset(
            resource_id=resource_id, ckan_instance=ckan_instance
        )
        return {"message": f"{resource_id} deleted successfully"}

    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail="Resource not found")
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Pre-CKAN server is not configured or unreachable.",
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.delete(
    "/resource/{resource_name}",
    response_model=dict,
    summary="Delete a resource",
    description="Delete a resource by its type and name.",
    responses={
        200: {
            "description": "Resource deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Resource deleted successfully"}
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
                "application/json": {"example": {"detail": "Resource not found"}}
            },
        },
    },
)
async def delete_resource_by_name(
    resource_name: str,
    server: Literal["local", "pre_ckan"] = Query(
        "local", description="Choose 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
):
    """
    Endpoint to delete a dataset by its name.

    If ?server=pre_ckan is provided and pre_ckan is enabled, deletes from
    the pre-CKAN instance. Otherwise defaults to local CKAN.
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

        dataset_services.delete_dataset(
            dataset_name=resource_name, ckan_instance=ckan_instance
        )
        return {"message": f"{resource_name} deleted successfully"}

    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail="Resource not found")
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Pre-CKAN server is not configured or unreachable.",
            )
        raise HTTPException(status_code=400, detail=error_msg)
