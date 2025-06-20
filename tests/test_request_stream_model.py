# tests/test_request_stream_model.py
from api.models.request_stream_model import ProducerPayload


class TestProducerPayload:
    """Test cases for ProducerPayload model."""

    def test_producer_payload_default_values(self):
        """Test ProducerPayload with default values."""
        payload = ProducerPayload()

        assert payload.keywords is None
        assert payload.match_all is False
        assert payload.filter_semantics == []

    def test_producer_payload_all_fields(self):
        """Test ProducerPayload with all fields provided."""
        payload = ProducerPayload(
            keywords="temperature,humidity,pressure",
            match_all=True,
            filter_semantics=["temp>20", "humidity<=50", "pressure>1000"],
        )

        assert payload.keywords == "temperature,humidity,pressure"
        assert payload.match_all is True
        assert payload.filter_semantics == ["temp>20", "humidity<=50", "pressure>1000"]

    def test_producer_payload_partial_fields(self):
        """Test ProducerPayload with partial fields."""
        payload = ProducerPayload(keywords="bme280", match_all=True)

        assert payload.keywords == "bme280"
        assert payload.match_all is True
        assert payload.filter_semantics == []

    def test_producer_payload_serialization(self):
        """Test ProducerPayload model serialization."""
        payload = ProducerPayload(
            keywords="test,data", match_all=True, filter_semantics=["value>10"]
        )

        # Test that it can be serialized to dict
        payload_dict = payload.model_dump()

        assert payload_dict["keywords"] == "test,data"
        assert payload_dict["match_all"] is True
        assert payload_dict["filter_semantics"] == ["value>10"]

    def test_producer_payload_from_dict(self):
        """Test ProducerPayload creation from dictionary."""
        data = {
            "keywords": "sensor1,sensor2",
            "match_all": False,
            "filter_semantics": ["temp>25", "humidity<=60"],
        }

        payload = ProducerPayload(**data)

        assert payload.keywords == "sensor1,sensor2"
        assert payload.match_all is False
        assert payload.filter_semantics == ["temp>25", "humidity<=60"]
