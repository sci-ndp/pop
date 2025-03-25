# /api/routes/search_routes/search_datasource_route.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Literal
from api.services import datasource_services
from api.models import DataSourceResponse
from api.config.ckan_settings import ckan_settings  # Import CKAN settings

router = APIRouter()


@router.get(
    "/search",
    response_model=List[DataSourceResponse],
    summary="Search datasets by terms",
    description=(
        "Search CKAN datasets by providing a list of terms.\n\n"
        "### Parameters\n"
        "- **terms**: A list of terms to search for in the datasets.\n"
        "- **keys**: An optional list specifying the keys "
        "to search each term.\n"
        "- **server**: Specify the server to search on: 'local', "
        "'global'.\n"
        "  If 'local' CKAN is disabled, it is not allowed.\n"
        "  If no server is specified, the default value is 'global'."
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
        },
        422: {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Validation error details"
                    }
                }
            }
        }
    }
)
async def search_datasets(
    terms: List[str] = Query(
        ...,
        description="A list of terms to search for in the datasets."
    ),
    keys: Optional[List[Optional[str]]] = Query(
        None,
        description=(
            "An optional list of keys corresponding to each term. "
            "Use `null` for a global search of the term."
        )
    ),
    server: Literal['local', 'global'] = Query(
        'global',  # Default value is always 'global'
        description=(
            "Specify the server to search on: 'local' or "
            "'global'"
            "If 'local' CKAN is disabled, it cannot be used."
        )
    )
):
    """
    Endpoint to search datasets by a list of terms with optional key
    specifications.

    Parameters
    ----------
    terms : List[str]
        A list of terms to search for in the datasets.
    keys : Optional[List[Optional[str]]]
        An optional list specifying the keys to search each term.
        Use `null` for a global search of the term.
    server : Literal['local', 'global']
        Specify the server to search on: 'local' or 'global'.
        If 'local' CKAN is disabled, it is not allowed.
        If no server is specified, the default is 'global'.

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    HTTPException
        - 400: If the number of keys does not match the number of terms.
        - 400: If 'local' CKAN is disabled and selected.
        - 400: If 'pre-ckan' CKAN is selected.
        - 422: If required query parameters are missing.
    """

    # Ensure the number of keys matches the number of terms if provided
    if keys is not None and len(keys) != len(terms):
        raise HTTPException(
            status_code=400,
            detail=(
                "The number of keys must match the number of terms, or keys "
                "must be omitted."
            )
        )

    # Validate that 'local' server is only allowed when CKAN local is enabled
    if server == 'local' and not ckan_settings.ckan_local_enabled:
        raise HTTPException(
            status_code=400,
            detail="Local CKAN is disabled and cannot be used."
        )

    # Disallow 'pre_ckan' as a valid server option
    if server == 'pre_ckan':
        raise HTTPException(
            status_code=400,
            detail="'pre_ckan' server is not supported."
        )

    try:
        # Call the service function to perform the dataset search
        results = await datasource_services.search_datasets_by_terms(
            terms_list=terms,
            keys_list=keys,
            server=server
        )
        return results
    except HTTPException as he:
        # Re-raise FastAPI-specific exceptions
        raise he
    except Exception as e:
        # Catch-all error handler to return a user-friendly response
        raise HTTPException(status_code=400, detail=str(e))
