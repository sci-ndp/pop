# tests/test_list_organization.py
import pytest
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
        mock_list.assert_called_once_with(None, 'local')


def test_list_organizations_with_name():
    # Mock the 'list_organization' function with the 'name' parameter
    with patch(
        'api.services.organization_services.list_organization'
    ) as mock_list:
        mock_list.return_value = ["org1"]
        response = client.get("/organization", params={"name": "org1"})
        assert response.status_code == 200
        assert response.json() == ["org1"]
        mock_list.assert_called_once_with("org1", 'local')


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
        mock_list.assert_called_once_with(None, 'local')


@pytest.mark.parametrize("server_arg", ["pre_ckan"])
def test_list_organizations_pre_ckan(server_arg):
    """
    Ensure list_organization is called with 'pre_ckan'
    and returns the expected data.
    """
    with patch(
        'api.services.organization_services.list_organization'
    ) as mock_list:
        mock_list.return_value = ["pre_org1", "pre_org2"]
        response = client.get("/organization", params={"server": server_arg})
        assert response.status_code == 200
        assert response.json() == ["pre_org1", "pre_org2"]
        mock_list.assert_called_once_with(None, server_arg)
