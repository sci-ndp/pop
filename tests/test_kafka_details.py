from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import app

client = TestClient(app)


def test_kafka_details_route():
    # Mock the individual attributes of kafka_settings
    with patch('api.config.kafka_settings.kafka_host', new="localhost"), \
         patch('api.config.kafka_settings.kafka_port', new=9092), \
         patch('api.config.kafka_settings.kafka_connection', new=True):

        # Send GET request to the endpoint
        response = client.get("/status/kafka-details")

        # Assert the response
        assert response.status_code == 200
        assert response.json() == {
            "kafka_host": "localhost",
            "kafka_port": 9092,
            "kafka_connection": True
        }
