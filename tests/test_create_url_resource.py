from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch
from api.main import app
from api.services.keycloak_services.get_current_user import get_current_user

client = TestClient(app)


def test_create_url_resource_success():
    # Mock 'add_url' to simulate successful resource creation
    with patch('api.routes.register_routes.post_url.add_url') as mock_add_url:
        mock_add_url.return_value = "12345678-abcd-efgh-ijkl-1234567890ab"

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "resource_name": "test_resource",
            "resource_title": "Test Resource",
            "owner_org": "organization_id",
            "resource_url": "http://example.com/data.csv",
            "file_type": "CSV",
            "notes": "This is a test resource.",
            "extras": {"key1": "value1", "key2": "value2"},
            "mapping": {"field1": "mapping1", "field2": "mapping2"},
            "processing": {
                "delimiter": ",",
                "header_line": 1,
                "start_line": 2,
                "comment_char": "#"
            }
        }

        response = client.post("/url", json=data)
        assert response.status_code == 201
        assert response.json() == {
            "id": "12345678-abcd-efgh-ijkl-1234567890ab"
        }
        mock_add_url.assert_called_once_with(
            resource_name="test_resource",
            resource_title="Test Resource",
            owner_org="organization_id",
            resource_url="http://example.com/data.csv",
            file_type="CSV",
            notes="This is a test resource.",
            extras={"key1": "value1", "key2": "value2"},
            mapping={"field1": "mapping1", "field2": "mapping2"},
            processing={
                "delimiter": ",",
                "header_line": 1,
                "start_line": 2,
                "comment_char": "#"
            }
        )

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_create_url_resource_key_error():
    # Mock 'add_url' to raise a KeyError
    with patch('api.routes.register_routes.post_url.add_url') as mock_add_url:
        mock_add_url.side_effect = KeyError("reserved_key")

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "resource_name": "test_resource",
            "resource_title": "Test Resource",
            "owner_org": "organization_id",
            "resource_url": "http://example.com/data.csv",
            "file_type": "CSV",
            "extras": {"reserved_key": "value"}
        }

        response = client.post("/url", json=data)
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Reserved key error: 'reserved_key'"
        }

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_create_url_resource_value_error():
    # Mock 'add_url' to raise a ValueError
    with patch('api.routes.register_routes.post_url.add_url') as mock_add_url:
        mock_add_url.side_effect = ValueError("Invalid file_type")

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "resource_name": "test_resource",
            "resource_title": "Test Resource",
            "owner_org": "organization_id",
            "resource_url": "http://example.com/data.csv",
            "file_type": "CSV",  # Use a valid file_type
            "extras": {"key1": "value1"}
        }

        response = client.post("/url", json=data)
        assert response.status_code == 400  # Bad Request
        assert response.json() == {
            "detail": "Invalid input: Invalid file_type"
        }

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_create_url_resource_general_exception():
    # Mock 'add_url' to raise a general Exception
    with patch('api.routes.register_routes.post_url.add_url') as mock_add_url:
        mock_add_url.side_effect = Exception("Unexpected error")

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "resource_name": "test_resource",
            "resource_title": "Test Resource",
            "owner_org": "organization_id",
            "resource_url": "http://example.com/data.csv",
            "file_type": "CSV",
            "extras": {"key1": "value1"}
        }

        response = client.post("/url", json=data)
        assert response.status_code == 400
        assert response.json() == {"detail": "Unexpected error"}

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_create_url_resource_validation_error():
    # Override 'get_current_user' dependency
    def mock_get_current_user():
        return {"user": "test_user"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

    data = {
        # Missing 'resource_name' to trigger validation error
        "resource_title": "Test Resource",
        "owner_org": "organization_id",
        "resource_url": "http://example.com/data.csv",
        "file_type": "CSV",
        "extras": {"key1": "value1"}
    }

    response = client.post("/url", json=data)
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["loc"] == ["body", "resource_name"]

    # Clean up dependency overrides
    app.dependency_overrides.pop(get_current_user, None)


def test_create_url_resource_unauthorized():
    # Override 'get_current_user' dependency to simulate unauthorized access
    def mock_get_current_user():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[get_current_user] = mock_get_current_user

    data = {
        "resource_name": "test_resource",
        "resource_title": "Test Resource",
        "owner_org": "organization_id",
        "resource_url": "http://example.com/data.csv",
        "file_type": "CSV",
        "extras": {"key1": "value1"}
    }

    response = client.post("/url", json=data)
    assert response.status_code == 401  # Unauthorized
    assert response.json() == {"detail": "Not authenticated"}

    # Clean up dependency overrides
    app.dependency_overrides.pop(get_current_user, None)
