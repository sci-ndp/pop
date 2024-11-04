from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import app
from api.services.keycloak_services.get_current_user import get_current_user

client = TestClient(app)


def test_create_s3_resource_success():
    # Mock 'add_s3' to simulate successful resource creation
    with patch('api.routes.register_routes.post_s3.add_s3') as mock_add_s3:
        mock_add_s3.return_value = "12345678-abcd-efgh-ijkl-1234567890ab"

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "resource_name": "test_resource",
            "resource_title": "Test Resource",
            "owner_org": "organization_id",
            "resource_s3": "s3://bucket/path/to/object",
            "notes": "This is a test resource.",
            "extras": {"key1": "value1", "key2": "value2"}
        }

        response = client.post("/s3", json=data)
        assert response.status_code == 201
        assert response.json() == {
            "id": "12345678-abcd-efgh-ijkl-1234567890ab"
        }
        mock_add_s3.assert_called_once_with(
            resource_name="test_resource",
            resource_title="Test Resource",
            owner_org="organization_id",
            resource_s3="s3://bucket/path/to/object",
            notes="This is a test resource.",
            extras={"key1": "value1", "key2": "value2"}
        )

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)
