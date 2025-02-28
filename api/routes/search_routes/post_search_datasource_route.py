# api/routes/search_routes/post_search_datasource_route.py
# English comments, PEP-8 lines <=79 chars

from fastapi import APIRouter, HTTPException
from typing import List
from api.services import datasource_services
from api.models import DataSourceResponse, SearchRequest

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
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "12345678-abcd-efgh-ijkl-1234567890ab",
                            "name": "example_dataset_name",
                            "title": "Example Dataset Title",
                            "owner_org": "example_org_name",
                            "description": "This is an example dataset.",
                            "resources": [
                                {
                                    "id": "abcd1234-efgh5678-ijkl9012",
                                    "url": "http://example.com/resource",
                                    "name": "Example Resource Name",
                                    "description": "This is an example.",
                                    "format": "CSV"
                                }
                            ],
                            "extras": {
                                "key1": "value1",
                                "key2": "value2"
                            }
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error message explaining the bad request"
                    }
                }
            }
        }
    }
)
async def search_datasource(data: SearchRequest):
    """
    Search by various parameters.

    Parameters
    ----------
    data : SearchRequest
        An object containing the parameters of the search

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    HTTPException
        If there is an error searching for the datasets, an HTTPException
        is raised with a detailed message.
    """
    # Convert resource_format to lowercase if provided
    if data.resource_format:
        data.resource_format = data.resource_format.lower()

    try:
        results = await datasource_services.search_datasource(
            **data.model_dump()
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
