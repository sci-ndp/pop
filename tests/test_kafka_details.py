# tests/test_kafka_details.py
from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import app
from api.config.kafka_settings import kafka_settings

client = TestClient(app)

def test_kafka_details_route():
    with patch.object(kafka_settings, 'kafka_host', new="localhost"), \
         patch.object(kafka_settings, 'kafka_port', new=9092), \
         patch.object(kafka_settings, 'kafka_connection', new=True), \
         patch.object(kafka_settings, 'kafka_prefix', new="data_stream_"), \
         patch.object(kafka_settings, 'max_streams', new=10):

        response = client.get("/status/kafka-details")
        assert response.status_code == 200
        assert response.json() == {
            "kafka_host": "localhost",
            "kafka_port": 9092,
            "kafka_connection": True,
            "kafka_prefix": "data_stream_",
            "max_streams": 10
        }
