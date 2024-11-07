from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api.main import app  # Adjust the import as necessary

client = TestClient(app)


def test_search_datasets_no_terms():
    """
    Test calling the /search endpoint without providing 'terms' parameter.

    Expected behavior:
    - The API should return a 422 Unprocessable Entity error indicating
      that the 'terms' parameter is required.
    """
    response = client.get("/search")
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "terms"],
                "msg": "Field required",
                "type": "missing",
                "input": None
            }
        ]
    }


def test_search_datasets_with_terms():
    """
    Test calling the /search endpoint with valid 'terms' and 'server'
    parameters.

    Expected behavior:
    - The API should return a 200 OK status.
    - The response should contain the mocked datasets.
    - The 'search_datasets_by_terms' function should be called with the correct
      parameters.
    """
    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = [
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

        # Prepare the query parameters
        params = [
            ("terms", "example"),
            ("terms", "dataset"),
            ("server", "global")
        ]

        response = client.get("/search", params=params)
        assert response.status_code == 200
        assert response.json() == mock_search.return_value

        mock_search.assert_awaited_once_with(
            terms_list=["example", "dataset"],
            server="global"
        )


def test_search_datasets_exception():
    """
    Test handling of exceptions in the /search endpoint.

    Expected behavior:
    - If the 'search_datasets_by_terms' function raises an exception,
      the API should return a 400 Bad Request status with the exception
      message.
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
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Error message explaining the bad request"
        }

        mock_search.assert_awaited_once_with(
            terms_list=["example"],
            server="local"
        )


def test_search_datasets_invalid_server():
    """
    Test calling the /search endpoint with an invalid 'server' parameter.

    Expected behavior:
    - The API should return a 422 Unprocessable Entity error indicating
      that the 'server' value is not valid.
    """
    params = [
        ("terms", "example"),
        ("server", "invalid_server")
    ]

    response = client.get("/search", params=params)
    assert response.status_code == 422  # Unprocessable Entity

    expected_error_detail = {
        "loc": ["query", "server"],
        "msg": "Input should be 'local' or 'global'",
        "type": "literal_error",
        "input": "invalid_server",
        "ctx": {"expected": "'local' or 'global'"}
    }

    assert response.json()["detail"][0] == expected_error_detail


def test_search_datasets_empty_terms():
    """
    Test calling the /search endpoint with an empty 'terms' parameter.

    Expected behavior:
    - The API should accept the request and return an empty list of datasets.
    - The 'search_datasets_by_terms' function should be called with an empty
    list.
    """
    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = []

        params = [("terms", "")]

        response = client.get("/search", params=params)
        assert response.status_code == 200
        assert response.json() == []

        mock_search.assert_awaited_once_with(
            terms_list=[""],
            server="local"
        )
