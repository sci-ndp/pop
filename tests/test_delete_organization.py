# tests/test_delete_organization.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, ANY
from api.main import app
from api.config.ckan_settings import ckan_settings

# Skip every test in this file if local CKAN is disabled
pytestmark = pytest.mark.skipif(
    not ckan_settings.ckan_local_enabled,
    reason="Local CKAN is disabled; skipping organization deletion tests."
)

client = TestClient(app)


def test_delete_organization_success():
    """
    Test that an organization is successfully deleted, returning 200.
    """
    with patch(
        'api.services.organization_services.delete_organization'
    ) as mock_delete:
        mock_delete.return_value = None  # No exception => success

        organization_name = "test_organization"
        response = client.delete(f"/organization/{organization_name}")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Organization deleted successfully"
        }
        # Accept that ckan_instance is also passed
        mock_delete.assert_called_once_with(
            organization_name=organization_name,
            ckan_instance=ANY
        )


def test_delete_organization_not_found():
    """
    Test that a non-existent organization returns a 404 status.
    """
    with patch(
        'api.services.organization_services.delete_organization'
    ) as mock_delete:
        mock_delete.side_effect = Exception("Organization not found")

        organization_name = "nonexistent_organization"
        response = client.delete(f"/organization/{organization_name}")
        # The route now returns 404 if "Organization not found"
        assert response.status_code == 404
        assert response.json() == {"detail": "Organization not found"}

        mock_delete.assert_called_once_with(
            organization_name=organization_name,
            ckan_instance=ANY
        )


def test_delete_organization_error():
    """
    Test that a general error in deleting the organization returns 400.
    """
    with patch(
        'api.services.organization_services.delete_organization'
    ) as mock_delete:
        mock_delete.side_effect = Exception("An unexpected error occurred")

        organization_name = "test_organization"
        response = client.delete(f"/organization/{organization_name}")
        assert response.status_code == 400
        assert response.json() == {"detail": "An unexpected error occurred"}

        mock_delete.assert_called_once_with(
            organization_name=organization_name,
            ckan_instance=ANY
        )
