# tests\test_search_datasource.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api.main import app


client = TestClient(app)


@pytest.mark.asyncio
async def test_search_datasets_no_terms():
    """
    Test the /search endpoint without providing the 'terms' parameter.

    Expected behavior:
    - The API should return a 422 Unprocessable Entity error indicating
      that the 'terms' parameter is required.
    """
    response = client.get("/search")
    assert response.status_code == 422, (
        "Expected a 422 status code for missing 'terms'"
    )
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "terms"],
                "msg": "Field required",
                "type": "missing",
                "input": None
            }
        ]
    }, "Response body does not match the expected error detail."


@pytest.mark.asyncio
async def test_search_datasets_with_terms():
    """
    Test the /search endpoint with valid 'terms' and 'server' parameters.

    Expected behavior:
    - The API should return 200 OK.
    - The response should contain the mocked datasets.
    - The 'search_datasets_by_terms' function should be called with
      correct parameters.
    """
    mock_result = [
        {
            "id": "12345678-abcd-efgh-ijkl-1234567890ab",
            "name": "example_dataset_name",
            "title": "Example Dataset Title",
            "owner_org": "example_org_name",
            "notes": "This is an example dataset.",
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

    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = mock_result

        params = [
            ("terms", "example"),
            ("terms", "dataset"),
            ("server", "global")
        ]

        response = client.get("/search", params=params)
        assert response.status_code == 200, (
            "Expected 200 status for valid 'terms'"
        )
        assert response.json() == mock_result, (
            "Response does not match mock data"
        )

        mock_search.assert_awaited_once_with(
            terms_list=["example", "dataset"],
            keys_list=None,
            server="global"
        )


@pytest.mark.asyncio
async def test_search_datasets_exception():
    """
    Test how the /search endpoint handles exceptions raised during the
    search.

    Expected behavior:
    - If 'search_datasets_by_terms' raises an exception, the API should
      return a 400 Bad Request with the exception message.
    """
    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.side_effect = Exception(
            "Error message explaining the bad request"
        )

        params = [("terms", "example")]

        response = client.get("/search", params=params)
        assert response.status_code == 400, (
            "Expected 400 status on exception"
        )
        assert response.json() == {
            "detail": "Error message explaining the bad request"
        }, "Error detail does not match the expected message."

        mock_search.assert_awaited_once_with(
            terms_list=["example"],
            keys_list=None,
            server="local"
        )


@pytest.mark.asyncio
async def test_search_datasets_invalid_server():
    """
    Test the /search endpoint with an invalid 'server' parameter.

    Expected behavior:
    - The API should return 422 Unprocessable Entity with an appropriate
      error.
    """
    params = [("terms", "example"), ("server", "invalid_server")]

    response = client.get("/search", params=params)
    assert response.status_code == 422, (
        "Expected 422 for invalid server value."
    )

    actual_error_detail = response.json()["detail"][0]

    assert actual_error_detail["loc"] == ["query", "server"]
    assert actual_error_detail["msg"] == (
        "Input should be 'local', 'global' or 'pre_ckan'")


@pytest.mark.asyncio
async def test_search_datasets_empty_terms():
    """
    Test the /search endpoint with an empty 'terms' parameter.

    Expected behavior:
    - The API should accept the request and return an empty list.
    - 'search_datasets_by_terms' should be called with an empty string
      in terms.
    """
    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = []

        params = [("terms", "")]

        response = client.get("/search", params=params)
        assert response.status_code == 200, (
            "Expected 200 status for empty terms."
        )
        assert response.json() == [], "Expected an empty list of datasets."

        mock_search.assert_awaited_once_with(
            terms_list=[""],
            keys_list=None,
            server="local"
        )


@pytest.mark.asyncio
async def test_search_datasets_with_keys():
    """
    Test the /search endpoint with 'terms' and 'keys' parameters.

    Expected behavior:
    - The API should return 200 OK.
    - The response should contain the mocked datasets.
    - 'search_datasets_by_terms' should be called with the specified keys.
    """
    mock_result = [
        {
            "id": "87654321-dcba-hgfe-lkji-0987654321ba",
            "name": "another_example_dataset",
            "title": "Another Example Dataset",
            "owner_org": "another_example_org",
            "notes": "This is another example dataset.",
            "resources": [],
            "extras": {}
        }
    ]

    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = mock_result

        params = [
            ("terms", "another"),
            ("terms", "dataset"),
            ("keys", "description"),
            ("keys", "extras.key1")
        ]

        response = client.get("/search", params=params)
        assert response.status_code == 200, (
            "Expected 200 for valid keys."
        )
        assert response.json() == mock_result, (
            "Response does not match mock data."
        )

        mock_search.assert_awaited_once_with(
            terms_list=["another", "dataset"],
            keys_list=["description", "extras.key1"],
            server="local"
        )


@pytest.mark.asyncio
async def test_search_datasets_mixed_keys():
    """
    Test the /search endpoint with mixed global and key-specific terms.

    Expected behavior:
    - The API should return 200 OK.
    - The response should contain the mocked datasets.
    - 'search_datasets_by_terms' should be called with 'null' for
      global terms.
    """
    mock_result = [
        {
            "id": "abcdef12-3456-7890-abcd-ef1234567890",
            "name": "mixed_search_dataset",
            "title": "Mixed Search Dataset",
            "owner_org": "mixed_org",
            "notes": "Dataset matching global and specific terms.",
            "resources": [],
            "extras": {}
        }
    ]

    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = mock_result

        params = [
            ("terms", "global_term"),
            ("terms", "specific_term"),
            ("keys", "null"),
            ("keys", "description")
        ]

        response = client.get("/search", params=params)
        assert response.status_code == 200, (
            "Expected 200 for mixed keys."
        )
        assert response.json() == mock_result, (
            "Response does not match mock data."
        )

        mock_search.assert_awaited_once_with(
            terms_list=["global_term", "specific_term"],
            keys_list=["null", "description"],
            server="local"
        )


@pytest.mark.asyncio
async def test_search_datasets_keys_length_mismatch():
    """
    Test that an error is returned when the number of keys does not match
    the number of terms.
    """
    response = client.get(
        "/search",
        params=[
            ("terms", "water"),
            ("terms", "temperature"),
            ("keys", "description")
        ]
    )
    assert response.status_code == 400, (
        "Expected 400 for mismatched keys/terms."
    )
    assert response.json() == {
        "detail": (
            "The number of keys must match the number of terms, "
            "or keys must be omitted."
        )
    }, "Error message does not match expected detail."


@pytest.mark.asyncio
async def test_search_datasets_special_chars_in_keys():
    """
    Test the /search endpoint when keys contain special characters that must
    be escaped for Solr.

    Expected behavior:
    - The API should not return a 400 error due to query syntax.
    - The endpoint should return a 200 OK and possibly no datasets if none
      match.
    """
    mock_result = []

    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = mock_result

        params = [
            ("terms", "example"),
            ("keys", "metadata[field]")
        ]

        response = client.get("/search", params=params)
        assert response.status_code == 200, (
            "Expected 200 for special chars in keys."
        )
        assert response.json() == mock_result, "Expected no results."

        mock_search.assert_awaited_once_with(
            terms_list=["example"],
            keys_list=["metadata[field]"],
            server="local"
        )
