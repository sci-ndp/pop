# api/routes/search_routes/post_search_datasource_route.py

from typing import List

from fastapi import APIRouter, HTTPException

from api.config.ckan_settings import ckan_settings
from api.models import DataSourceResponse, SearchRequest
from api.services import datasource_services

router = APIRouter()


@router.post(
    "/search",
    response_model=List[DataSourceResponse],
    summary="Search data sources",
    description=(
        "Search datasets by various parameters.\n\n"
        "### Common registration-matching parameters\n"
        "- **dataset_name**: the name of the dataset\n"
        "- **dataset_title**: the title of the dataset\n"
        "- **owner_org**: the name of the organization\n"
        "- **resource_url**: the URL of the dataset resource\n"
        "- **resource_name**: the name of the dataset resource\n"
        "- **dataset_description**: the description of the dataset\n"
        "- **resource_description**: the description of the resource\n"
        "- **resource_format**: the format of the dataset resource\n\n"
        "### User-defined value search parameters\n"
        "- **search_term**: a comma-separated list of terms to search "
        "across all fields\n"
        "- **filter_list**: a list of field filters of the form "
        "`key:value`.\n"
        "- **timestamp**: a filter on the `timestamp` field of results.\n\n"
        "### Server selection\n"
        "By default, 'server' can be one of `local` or `global`. "
        "Optionally, `pre_ckan` is also supported if enabled.\n\n"
        "### Examples\n"
        "1) Searching by dataset_name and resource_format.\n"
        "2) Providing multiple comma-separated terms in 'search_term'."
    ),
    responses={
        200: {
            "description": "Datasets retrieved successfully",
        },
        400: {"description": "Bad Request"},
    },
)
async def search_datasource(data: SearchRequest) -> List[DataSourceResponse]:
    """
    Search by various parameters, including an optional 'pre_ckan' server.

    Raises
    ------
    HTTPException
        - 400: if 'pre_ckan' is disabled or unreachable.
    """
    # If server is 'pre_ckan' but not enabled, raise a 400 error
    if data.server == "pre_ckan" and not ckan_settings.pre_ckan_enabled:
        raise HTTPException(
            status_code=400, detail="Pre-CKAN is disabled and cannot be used."
        )

    # Convert 'resource_format' to lowercase if it's provided
    if data.resource_format:
        data.resource_format = data.resource_format.lower()

    try:
        results = await datasource_services.search_datasource(**data.model_dump())
        return results

    except Exception as exc:
        error_text = str(exc)
        # Provide a friendly error if CKAN complains about the scheme
        if "No scheme supplied" in error_text:
            raise HTTPException(
                status_code=400, detail="Server is not configured or unreachable."
            )
        raise HTTPException(status_code=400, detail=error_text)
