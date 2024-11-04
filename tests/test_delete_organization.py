from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import app  # Import your FastAPI application

client = TestClient(app)


def test_delete_organization_success():
    # Mock the 'delete_organization' function to simulate successful deletion
    with patch(
        'api.services.organization_services.delete_organization'
    ) as mock_delete:
        mock_delete.return_value = None  # No exception means success
        organization_name = "test_organization"
        response = client.delete(f"/organization/{organization_name}")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Organization deleted successfully"}
        mock_delete.assert_called_once_with(organization_name)


def test_delete_organization_not_found():
    # Mock the 'delete_organization' function to raise an exception for not
    # found
    with patch(
        'api.services.organization_services.delete_organization'
    ) as mock_delete:
        mock_delete.side_effect = Exception("Organization not found")
        organization_name = "nonexistent_organization"
        response = client.delete(f"/organization/{organization_name}")
        assert response.status_code == 400
        assert response.json() == {"detail": "Organization not found"}
        mock_delete.assert_called_once_with(organization_name)


def test_delete_organization_error():
    # Mock the 'delete_organization' function to raise a general exception
    with patch(
        'api.services.organization_services.delete_organization'
    ) as mock_delete:
        mock_delete.side_effect = Exception("An unexpected error occurred")
        organization_name = "test_organization"
        response = client.delete(f"/organization/{organization_name}")
        assert response.status_code == 400
        assert response.json() == {"detail": "An unexpected error occurred"}
        mock_delete.assert_called_once_with(organization_name)
