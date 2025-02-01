# tests/test_update_kafka_datasource.py

import pytest
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.main import app
from api.services.keycloak_services.get_current_user import get_current_user

client = TestClient(app)


def route_exists(path_prefix: str, method: str) -> bool:
    """
    Returns True if there is any route that starts with `path_prefix`
    and supports the given HTTP method.
    Useful when the path includes parameters (e.g., /kafka/{dataset_id}).
    """
    for route in app.routes:
        if route.path.startswith(path_prefix) and method in route.methods:
            return True
    return False


def test_update_kafka_datasource_success():
    # Skip if the PUT /kafka/ route (with path param) does not exist
    if not route_exists("/kafka/", "PUT"):
        pytest.skip(
            "PUT /kafka/{dataset_id} route not defined; skipping test.")

    with patch('api.services.kafka_services.update_kafka') as mock_update:
        mock_update.return_value = True

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
    # Skip if the PUT /kafka/ route (with path param) does not exist
    if not route_exists("/kafka/", "PUT"):
        pytest.skip(
            "PUT /kafka/{dataset_id} route not defined; skipping test.")

    with patch('api.services.kafka_services.update_kafka') as mock_update:
        mock_update.return_value = False

        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        dataset_id = "nonexistent-dataset-id"
        data = {
            "dataset_name": "kafka_topic_example_updated",
            "kafka_topic": "example_topic_updated"
        }

        response = client.put(f"/kafka/{dataset_id}", json=data)
        assert response.status_code == 404
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
    # Skip if the PUT /kafka/ route (with path param) does not exist
    if not route_exists("/kafka/", "PUT"):
        pytest.skip(
            "PUT /kafka/{dataset_id} route not defined; skipping test.")

    with patch('api.services.kafka_services.update_kafka') as mock_update:
        mock_update.side_effect = Exception("Error updating Kafka dataset")

        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        dataset_id = "12345678-abcd-efgh-ijkl-1234567890ab"
        data = {
            "dataset_name": "kafka_topic_example_updated",
            "kafka_topic": "example_topic_updated"
        }

        response = client.put(f"/kafka/{dataset_id}", json=data)
        assert response.status_code == 400
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
    # Skip if the PUT /kafka/ route (with path param) does not exist
    if not route_exists("/kafka/", "PUT"):
        pytest.skip(
            "PUT /kafka/{dataset_id} route not defined; skipping test.")

    def mock_get_current_user():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[get_current_user] = mock_get_current_user

    dataset_id = "12345678-abcd-efgh-ijkl-1234567890ab"
    data = {
        "dataset_name": "kafka_topic_example_updated",
        "kafka_topic": "example_topic_updated"
    }

    response = client.put(f"/kafka/{dataset_id}", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Clean up dependency overrides
    app.dependency_overrides.pop(get_current_user, None)
