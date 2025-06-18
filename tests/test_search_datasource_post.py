# tests/test_search_datasource_post.py
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_search_datasource_valid_request():
    # Mock the 'search_datasource' function for a valid request
    with patch(
        "api.services.datasource_services.search_datasource", new_callable=AsyncMock
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
                        "format": "CSV",
                    }
                ],
                "extras": {"key1": "value1", "key2": "value2"},
            }
        ]
        data = {
            "dataset_name": "example_dataset_name",
            "resource_format": "CSV",
            "server": "global",
        }
        response = client.post("/search", json=data)
        assert response.status_code == 200
        assert response.json() == mock_search.return_value
        mock_search.assert_awaited_once_with(
            dataset_name="example_dataset_name",
            dataset_title=None,
            owner_org=None,
            resource_url=None,
            resource_name=None,
            dataset_description=None,
            resource_description=None,
            resource_format="csv",
            search_term=None,
            filter_list=None,
            timestamp=None,
            server="global",
        )


def test_search_datasource_exception():
    # Mock the 'search_datasource' function to raise an exception
    with patch(
        "api.services.datasource_services.search_datasource", new_callable=AsyncMock
    ) as mock_search:
        mock_search.side_effect = Exception("Error message explaining the bad request")
        data = {"dataset_name": "example_dataset_name"}
        response = client.post("/search", json=data)
        assert response.status_code == 400
        assert response.json() == {"detail": "Error message explaining the bad request"}
        mock_search.assert_awaited_once_with(
            dataset_name="example_dataset_name",
            dataset_title=None,
            owner_org=None,
            resource_url=None,
            resource_name=None,
            dataset_description=None,
            resource_description=None,
            resource_format=None,
            search_term=None,
            filter_list=None,
            timestamp=None,
            server="global",
        )
