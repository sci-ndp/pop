from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import app

client = TestClient(app)


def test_kafka_details_route():
    # Mock the individual attributes of kafka_settings
    with (
        patch(
            'api.config.kafka_settings.kafka_settings.kafka_host',
            new="localhost"),
        patch(
            'api.config.kafka_settings.kafka_settings.kafka_port',
            new=9092),
        patch(
            'api.config.kafka_settings.kafka_settings.kafka_connection',
            new=True),
        patch(
            'api.config.kafka_settings.kafka_settings.kafka_prefix',
            new="data_stream_"),
        patch(
            'api.config.kafka_settings.kafka_settings.max_streams',
            new=10)):

        # Send GET request to the endpoint
        response = client.get("/status/kafka-details")

        # Assert the response
        assert response.status_code == 200
        assert response.json() == {
            "kafka_host": "localhost",
            "kafka_port": 9092,
            "kafka_connection": True,
            "kafka_prefix": "data_stream_",
            "max_streams": 10
        }
