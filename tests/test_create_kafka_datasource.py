from fastapi.testclient import TestClient
from fastapi import HTTPException
from api.main import app
from api.services.keycloak_services.get_current_user import get_current_user
from unittest.mock import patch

client = TestClient(app)


def test_create_kafka_datasource_success():
    # Mock 'kafka_services.add_kafka' to simulate successful creation
    with patch('api.services.kafka_services.add_kafka') as mock_add_kafka:
        mock_add_kafka.return_value = "12345678-abcd-efgh-ijkl-1234567890ab"

        # Override 'get_current_user' dependency
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
            "dataset_description": (
                "This is an example Kafka topic."
            ),
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
            dataset_description=(
                "This is an example Kafka topic."
            ),
            extras={"key1": "value1", "key2": "value2"},
            mapping={"field1": "mapping1", "field2": "mapping2"},
            processing={"data_key": "data", "info_key": "info"}
        )

        # Clean up the override
        app.dependency_overrides.pop(get_current_user, None)


def test_create_kafka_datasource_unauthorized():
    # Override 'get_current_user' dependency to simulate unauthorized access
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
    assert response.status_code == 401  # Unauthorized
    assert response.json() == {"detail": "Not authenticated"}

    # Clean up the override
    app.dependency_overrides.pop(get_current_user, None)


def test_create_kafka_datasource_bad_request():
    # Mock 'kafka_services.add_kafka' to raise an exception
    with patch('api.services.kafka_services.add_kafka') as mock_add_kafka:
        mock_add_kafka.side_effect = Exception("Error creating Kafka dataset")

        # Override 'get_current_user' dependency
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
    # Override 'get_current_user' dependency
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
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["loc"] == ["body", "dataset_name"]

    # Clean up the override
    app.dependency_overrides.pop(get_current_user, None)
