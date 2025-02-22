import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch
from api.main import app
from api.services.keycloak_services.get_current_user import get_current_user
from api.config.ckan_settings import ckan_settings

# Skip every test in this file if local CKAN is disabled
pytestmark = pytest.mark.skipif(
    not ckan_settings.ckan_local_enabled,
    reason="Local CKAN is disabled; skipping organization deletion tests."
)


client = TestClient(app)


def test_create_organization_success():
    # Mock 'organization_services.create_organization' for successful creation
    with patch(
        'api.services.organization_services.create_organization') as \
            mock_create:
        mock_create.return_value = "305284e6-6338-4e13-b39b-e6efe9f1c45a"

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "name": "test_organization",
            "title": "Test Organization",
            "description": "An organization for testing purposes."
        }

        response = client.post("/organization", json=data)
        assert response.status_code == 201
        assert response.json() == {
            "id": "305284e6-6338-4e13-b39b-e6efe9f1c45a",
            "message": "Organization created successfully"
        }
        mock_create.assert_called_once_with(
            name="test_organization",
            title="Test Organization",
            description="An organization for testing purposes."
        )

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_create_organization_already_exists():
    # Mock 'organization_services.create_organization' to raise an exception
    with patch(
        'api.services.organization_services.create_organization') as \
            mock_create:
        mock_create.side_effect = Exception(
            "Organization name already exists.")

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "name": "existing_organization",
            "title": "Existing Organization",
            "description": "An organization that already exists."
        }

        response = client.post("/organization", json=data)
        assert response.status_code == 400  # Bad Request
        assert response.json() == {
            "detail": "Organization name already exists."}
        mock_create.assert_called_once_with(
            name="existing_organization",
            title="Existing Organization",
            description="An organization that already exists."
        )

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_create_organization_unauthorized():
    # Override 'get_current_user' dependency to simulate unauthorized access
    def mock_get_current_user():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[get_current_user] = mock_get_current_user

    data = {
        "name": "test_organization",
        "title": "Test Organization",
        "description": "An organization for testing purposes."
    }

    response = client.post("/organization", json=data)
    assert response.status_code == 401  # Unauthorized
    assert response.json() == {"detail": "Not authenticated"}

    # Clean up dependency overrides
    app.dependency_overrides.pop(get_current_user, None)


def test_create_organization_validation_error():
    # Override 'get_current_user' dependency
    def mock_get_current_user():
        return {"user": "test_user"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

    data = {
        # Missing 'name' field to trigger validation error
        "title": "Test Organization",
        "description": "An organization for testing purposes."
    }

    response = client.post("/organization", json=data)
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["loc"] == ["body", "name"]

    # Clean up dependency overrides
    app.dependency_overrides.pop(get_current_user, None)
