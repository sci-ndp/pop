# /api/routes/search_routes/search_datasource_route.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Literal
from api.services import datasource_services
from api.models import DataSourceResponse

router = APIRouter()


@router.get(
    "/search",
    response_model=List[DataSourceResponse],
    summary="Search datasets by terms",
    description=(
        "Search CKAN datasets by providing a list of terms.\n\n"
        "### Parameters\n"
        "- **terms**: A list of terms to search for in the datasets.\n"
        "- **keys**: An optional list specifying the keys to search each "
        "term.\n"
        "- **server**: Specify the server to search on: 'local' or 'global'."
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
            "Use `null` for global search of the term."
        )
    ),
    server: Literal['local', 'global', 'pre_ckan'] = Query(
        'local',
        description=(
            "Specify the server to search on: "
            "'local', 'global', or 'pre_ckan'.")
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
        An optional list specifying the keys to search each term. Use `null`
        for global search of the term.
    server : Literal['local', 'global']
        Specify the server to search on: 'local' or 'global'.

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    HTTPException
        If there is an error searching for the datasets or validation fails.
    """
    if keys is not None and len(keys) != len(terms):
        raise HTTPException(
            status_code=400,
            detail=(
                "The number of keys must match the number of terms, or keys "
                "must be omitted.")
        )

    try:
        results = await datasource_services.search_datasets_by_terms(
            terms_list=terms,
            keys_list=keys,
            server=server
        )
        return results
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
