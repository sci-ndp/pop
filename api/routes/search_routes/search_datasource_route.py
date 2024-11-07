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
        }
    }
)
async def search_datasets(
    terms: List[str] = Query(
        ...,
        description="A list of terms to search for in the datasets."
    ),
    server: Optional[Literal['local', 'global']] = Query(
        'local',
        description="Specify the server to search on: 'local' or 'global'."
    )
):
    """
    Endpoint to search datasets by a list of terms.

    Parameters
    ----------
    terms : List[str]
        A list of terms to search for in the datasets.
    server : Optional[str]
        Specify the server to search on: 'local' or 'global'.

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    HTTPException
        If there is an error searching for the datasets, an HTTPException is
        raised with a detailed message.
    """
    try:
        results = await datasource_services.search_datasets_by_terms(
            terms_list=terms,
            server=server
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
