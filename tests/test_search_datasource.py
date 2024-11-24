from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api.main import app


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
      parameters, including 'keys_list=None'.
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
            keys_list=None,  # Explicitly pass None for keys_list
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
            keys_list=None,  # Explicitly pass None for keys_list
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
        "type": "type_error.enum",
        "ctx": {"enum_values": ["local", "global"]}
    }

    # Extract the first error detail
    actual_error_detail = response.json()["detail"][0]

    # Assert each component of the error detail
    assert actual_error_detail["loc"] == expected_error_detail["loc"]
    assert actual_error_detail["msg"] == expected_error_detail["msg"]


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
            keys_list=None,  # Explicitly pass None for keys_list
            server="local"
        )


def test_search_datasets_with_keys():
    """
    Test calling the /search endpoint with 'terms' and 'keys' parameters.

    Expected behavior:
    - The API should return a 200 OK status.
    - The response should contain the mocked datasets.
    - The 'search_datasets_by_terms' function should be called with the correct
      'keys_list'.
    """
    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = [
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

        # Prepare the query parameters with 'keys'
        params = [
            ("terms", "another"),
            ("terms", "dataset"),
            ("keys", "description"),
            ("keys", "extras.key1")
        ]

        response = client.get("/search", params=params)
        assert response.status_code == 200
        assert response.json() == mock_search.return_value

        mock_search.assert_awaited_once_with(
            terms_list=["another", "dataset"],
            keys_list=["description", "extras.key1"],
            server="local"
        )


def test_search_datasets_mixed_keys():
    """
    Test calling the /search endpoint with mixed global and key-specific
    searches.

    Expected behavior:
    - The API should return a 200 OK status.
    - The response should contain the mocked datasets.
    - The 'search_datasets_by_terms' function should be called with the correct
      'keys_list', including 'null' for global search terms.
    """
    with patch(
        'api.services.datasource_services.search_datasets_by_terms',
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = [
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

        # Prepare the query parameters with mixed 'keys'
        params = [
            ("terms", "global_term"),
            ("terms", "specific_term"),
            ("keys", "null"),
            ("keys", "description")
        ]

        response = client.get("/search", params=params)
        assert response.status_code == 200
        assert response.json() == mock_search.return_value

        # The service function receives 'keys_list=['null', 'description']'
        mock_search.assert_awaited_once_with(
            terms_list=["global_term", "specific_term"],
            keys_list=["null", "description"],  # Expect 'null' as string
            server="local"
        )


def test_search_datasets_keys_length_mismatch():
    """
    Test that an error is returned when keys and terms lengths do not match.
    """
    response = client.get(
        "/search",
        params=[
            ("terms", "water"),
            ("terms", "temperature"),
            ("keys", "description")  # Only one key for two terms
        ]
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "The number of keys must match the number of terms, "
        "or keys must be omitted."
    }
