# tests/test_update_kafka_datasource.py

from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch
from api.main import app
from api.services.keycloak_services.get_current_user import get_current_user

client = TestClient(app)


def test_update_kafka_datasource_success():
    # Mock 'update_kafka' to simulate successful update
    with patch('api.services.kafka_services.update_kafka') as mock_update:
        mock_update.return_value = True

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        dataset_id = "12345678-abcd-efgh-ijkl-1234567890ab"
        data = {
            "dataset_name": "kafka_topic_example_updated",
            "kafka_topic": "example_topic_updated"
        }

        response = client.put(f"/kafka/{dataset_id}", json=data)
        assert response.status_code == 200
        assert response.json() == {
            "message": "Kafka dataset updated successfully"
        }
        mock_update.assert_called_once_with(
            dataset_id=dataset_id,
            dataset_name="kafka_topic_example_updated",
            dataset_title=None,
            owner_org=None,
            kafka_topic="example_topic_updated",
            kafka_host=None,
            kafka_port=None,
            dataset_description=None,
            extras=None,
            mapping=None,
            processing=None
        )

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_update_kafka_datasource_not_found():
    # Mock 'update_kafka' to simulate dataset not found
    with patch('api.services.kafka_services.update_kafka') as mock_update:
        mock_update.return_value = False

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        dataset_id = "nonexistent-dataset-id"
        data = {
            "dataset_name": "kafka_topic_example_updated",
            "kafka_topic": "example_topic_updated"
        }

        response = client.put(f"/kafka/{dataset_id}", json=data)
        assert response.status_code == 404  # Not Found
        assert response.json() == {"detail": "Kafka dataset not found"}
        mock_update.assert_called_once_with(
            dataset_id=dataset_id,
            dataset_name="kafka_topic_example_updated",
            dataset_title=None,
            owner_org=None,
            kafka_topic="example_topic_updated",
            kafka_host=None,
            kafka_port=None,
            dataset_description=None,
            extras=None,
            mapping=None,
            processing=None
        )

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_update_kafka_datasource_bad_request():
    # Mock 'update_kafka' to raise an exception
    with patch('api.services.kafka_services.update_kafka') as mock_update:
        mock_update.side_effect = Exception(
            "Error updating Kafka dataset")

        # Override 'get_current_user' dependency
        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        dataset_id = "12345678-abcd-efgh-ijkl-1234567890ab"
        data = {
            "dataset_name": "kafka_topic_example_updated",
            "kafka_topic": "example_topic_updated"
        }

        response = client.put(f"/kafka/{dataset_id}", json=data)
        assert response.status_code == 400  # Bad Request
        assert response.json() == {"detail": "Error updating Kafka dataset"}
        mock_update.assert_called_once_with(
            dataset_id=dataset_id,
            dataset_name="kafka_topic_example_updated",
            dataset_title=None,
            owner_org=None,
            kafka_topic="example_topic_updated",
            kafka_host=None,
            kafka_port=None,
            dataset_description=None,
            extras=None,
            mapping=None,
            processing=None
        )

        # Clean up dependency overrides
        app.dependency_overrides.pop(get_current_user, None)


def test_update_kafka_datasource_unauthorized():
    # Override 'get_current_user' dependency to simulate unauthorized access
    def mock_get_current_user():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[get_current_user] = mock_get_current_user

    dataset_id = "12345678-abcd-efgh-ijkl-1234567890ab"
    data = {
        "dataset_name": "kafka_topic_example_updated",
        "kafka_topic": "example_topic_updated"
    }

    response = client.put(f"/kafka/{dataset_id}", json=data)
    assert response.status_code == 401  # Unauthorized
    assert response.json() == {"detail": "Not authenticated"}

    # Clean up dependency overrides
    app.dependency_overrides.pop(get_current_user, None)
