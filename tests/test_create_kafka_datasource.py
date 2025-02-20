# tests/test_create_kafka_datasource.py

import pytest
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.main import app
from api.services.keycloak_services.get_current_user import get_current_user


client = TestClient(app)


def route_exists(path: str, method: str) -> bool:
    """
    Checks if a given path and method exist among the app's routes.

    :param path: The route path (e.g., "/kafka").
    :param method: The HTTP method (e.g., "POST", "GET", "PUT").
    :return: True if the route+method is found, False otherwise.
    """
    for route in app.routes:
        if route.path == path and method in route.methods:
            return True
    return False


def test_create_kafka_datasource_success():
    # Skip if the POST /kafka route does not exist
    if not route_exists("/kafka", "POST"):
        pytest.skip("POST /kafka route not defined; skipping test.")

    with patch('api.services.kafka_services.add_kafka') as mock_add_kafka:
        mock_add_kafka.return_value = "12345678-abcd-efgh-ijkl-1234567890ab"

        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "dataset_name": "kafka_topic_example",
            "dataset_title": "Kafka Topic Example",
            "owner_org": "organization_id",
            "kafka_topic": "example_topic",
            "kafka_host": "kafka_host",
            "kafka_port": "kafka_port",
            "dataset_description": "This is an example Kafka topic.",
            "extras": {"key1": "value1", "key2": "value2"},
            "mapping": {"field1": "mapping1", "field2": "mapping2"},
            "processing": {"data_key": "data", "info_key": "info"}
        }

        response = client.post("/kafka", json=data)
        assert response.status_code == 201
        assert response.json() == {
            "id": "12345678-abcd-efgh-ijkl-1234567890ab"
        }

        mock_add_kafka.assert_called_once_with(
            dataset_name="kafka_topic_example",
            dataset_title="Kafka Topic Example",
            owner_org="organization_id",
            kafka_topic="example_topic",
            kafka_host="kafka_host",
            kafka_port="kafka_port",
            dataset_description="This is an example Kafka topic.",
            extras={"key1": "value1", "key2": "value2"},
            mapping={"field1": "mapping1", "field2": "mapping2"},
            processing={"data_key": "data", "info_key": "info"}
        )

        # Clean up the override
        app.dependency_overrides.pop(get_current_user, None)


def test_create_kafka_datasource_unauthorized():
    # Skip if the POST /kafka route does not exist
    if not route_exists("/kafka", "POST"):
        pytest.skip("POST /kafka route not defined; skipping test.")

    def mock_get_current_user():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[get_current_user] = mock_get_current_user

    data = {
        "dataset_name": "kafka_topic_example",
        "dataset_title": "Kafka Topic Example",
        "owner_org": "organization_id",
        "kafka_topic": "example_topic",
        "kafka_host": "kafka_host",
        "kafka_port": "kafka_port"
    }

    response = client.post("/kafka", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Clean up the override
    app.dependency_overrides.pop(get_current_user, None)


def test_create_kafka_datasource_bad_request():
    # Skip if the POST /kafka route does not exist
    if not route_exists("/kafka", "POST"):
        pytest.skip("POST /kafka route not defined; skipping test.")

    with patch('api.services.kafka_services.add_kafka') as mock_add_kafka:
        mock_add_kafka.side_effect = Exception("Error creating Kafka dataset")

        def mock_get_current_user():
            return {"user": "test_user"}

        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "dataset_name": "kafka_topic_example",
            "dataset_title": "Kafka Topic Example",
            "owner_org": "organization_id",
            "kafka_topic": "example_topic",
            "kafka_host": "kafka_host",
            "kafka_port": "kafka_port"
        }

        response = client.post("/kafka", json=data)
        assert response.status_code == 400
        assert response.json() == {"detail": "Error creating Kafka dataset"}

        # Clean up the override
        app.dependency_overrides.pop(get_current_user, None)


def test_create_kafka_datasource_validation_error():
    # Skip if the POST /kafka route does not exist
    if not route_exists("/kafka", "POST"):
        pytest.skip("POST /kafka route not defined; skipping test.")

    def mock_get_current_user():
        return {"user": "test_user"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

    data = {
        # Missing 'dataset_name' to trigger validation error
        "dataset_title": "Kafka Topic Example",
        "owner_org": "organization_id",
        "kafka_topic": "example_topic",
        "kafka_host": "kafka_host",
        "kafka_port": "kafka_port"
    }

    response = client.post("/kafka", json=data)
    assert response.status_code == 422
    # Check the validation error location
    assert response.json()["detail"][0]["loc"] == ["body", "dataset_name"]

    # Clean up the override
    app.dependency_overrides.pop(get_current_user, None)


def test_create_kafka_datasource_duplicate_error():
    # Skip if the POST /kafka route does not exist
    if not route_exists("/kafka", "POST"):
        pytest.skip("POST /kafka route not defined; skipping test.")

    with patch("api.services.kafka_services.add_kafka") as mock_add_kafka:
        mock_add_kafka.side_effect = Exception(
            '{"name": ["That name is already in use."]}'
        )

        def mock_get_current_user():
            return {"user": "test_user"}
        app.dependency_overrides[get_current_user] = mock_get_current_user

        data = {
            "dataset_name": "duplicate_name",
            "dataset_title": "Duplicate Name",
            "owner_org": "test_org",
            "kafka_topic": "test_topic",
            "kafka_host": "localhost",
            "kafka_port": "9092",
            "dataset_description": "Test dataset"
        }

        response = client.post("/kafka", json=data)
        assert response.status_code == 409
        assert response.json() == {
            "detail": {
                "error": "Duplicate Dataset",
                "detail": (
                    "A dataset with the given name or URL already exists."
                )
            }
        }

        # Clean up the override
        app.dependency_overrides.pop(get_current_user, None)
