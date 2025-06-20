# tests/test_list_organization.py
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.config.ckan_settings import ckan_settings
from api.main import app

client = TestClient(app)


def test_list_organizations_no_name():
    """
    Test that when no 'name' is provided and no 'server' is specified,
    the 'list_organization' function is called with (None, 'global').
    """
    with patch("api.services.organization_services.list_organization") as mock_list:
        mock_list.return_value = ["org1", "org2", "org3"]

        response = client.get("/organization")  # server defaults to 'global'
        assert response.status_code == 200
        assert response.json() == ["org1", "org2", "org3"]

        mock_list.assert_called_once_with(None, "global")


def test_list_organizations_with_name():
    """
    Test that when a 'name' is provided and no 'server' is specified,
    the 'list_organization' function is called with (name, 'global').
    """
    with patch("api.services.organization_services.list_organization") as mock_list:
        mock_list.return_value = ["org1"]

        response = client.get("/organization", params={"name": "org1"})
        assert response.status_code == 200
        assert response.json() == ["org1"]

        mock_list.assert_called_once_with("org1", "global")


def test_list_organizations_exception():
    """
    Test that if an exception occurs in 'list_organization', the endpoint
    returns status code 400 with the appropriate error detail.
    """
    with patch("api.services.organization_services.list_organization") as mock_list:
        mock_list.side_effect = Exception("Error message explaining the bad request")

        response = client.get("/organization")
        assert response.status_code == 400
        assert response.json() == {"detail": "Error message explaining the bad request"}

        mock_list.assert_called_once_with(None, "global")


@pytest.mark.parametrize("server_arg", ["pre_ckan"])
def test_list_organizations_pre_ckan(server_arg):
    """
    Test that when 'server=pre_ckan' is specified and pre_ckan is enabled,
    'list_organization' is called with (None, 'pre_ckan') and returns data.
    """
    with (
        patch.object(ckan_settings, "pre_ckan_enabled", True),
        patch("api.services.organization_services.list_organization") as mock_list,
    ):
        mock_list.return_value = ["pre_org1", "pre_org2"]

        response = client.get("/organization", params={"server": server_arg})
        assert response.status_code == 200
        assert response.json() == ["pre_org1", "pre_org2"]

        mock_list.assert_called_once_with(None, server_arg)
