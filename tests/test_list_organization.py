from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import app

client = TestClient(app)


def test_list_organizations_no_name():
    # Mock the 'list_organization' function without the 'name' parameter
    with patch(
        'api.services.organization_services.list_organization'
    ) as mock_list:
        mock_list.return_value = ["org1", "org2", "org3"]
        response = client.get("/organization")
        assert response.status_code == 200
        assert response.json() == ["org1", "org2", "org3"]
        mock_list.assert_called_once_with(None)


def test_list_organizations_with_name():
    # Mock the 'list_organization' function with the 'name' parameter
    with patch(
        'api.services.organization_services.list_organization'
    ) as mock_list:
        mock_list.return_value = ["org1"]
        response = client.get("/organization", params={"name": "org1"})
        assert response.status_code == 200
        assert response.json() == ["org1"]
        mock_list.assert_called_once_with("org1")


def test_list_organizations_exception():
    # Mock the 'list_organization' function to raise an exception
    with patch(
        'api.services.organization_services.list_organization'
    ) as mock_list:
        mock_list.side_effect = Exception(
            "Error message explaining the bad request"
        )
        response = client.get("/organization")
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Error message explaining the bad request"
        }
        mock_list.assert_called_once_with(None)
