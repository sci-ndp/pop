# tests/test_kafka_settings.py
from api.config.kafka_settings import KafkaSettings, kafka_settings


class TestKafkaSettings:
    """Test cases for KafkaSettings."""

    def test_kafka_settings_default_values(self):
        """Test KafkaSettings can be instantiated and has required attributes."""
        settings = KafkaSettings()

        # Just test that attributes exist, don't assume their values
        assert hasattr(settings, "kafka_connection")
        assert hasattr(settings, "kafka_host")
        assert hasattr(settings, "kafka_port")
        assert hasattr(settings, "kafka_prefix")
        assert hasattr(settings, "max_streams")
        assert isinstance(settings.kafka_port, int)
        assert isinstance(settings.kafka_host, str)

    def test_kafka_settings_connection_details_property(self):
        """Test the connection_details property."""
        settings = KafkaSettings()

        details = settings.connection_details

        assert isinstance(details, dict)
        assert "kafka_connection" in details
        assert "kafka_host" in details
        assert "kafka_port" in details
        assert "kafka_prefix" in details
        assert "max_streams" in details

    def test_kafka_settings_with_custom_values(self):
        """Test KafkaSettings with custom values."""
        settings = KafkaSettings(
            kafka_connection=True,
            kafka_host="kafka.example.com",
            kafka_port=9093,
            kafka_prefix="custom_",
            max_streams=20,
        )

        assert settings.kafka_connection is True
        assert settings.kafka_host == "kafka.example.com"
        assert settings.kafka_port == 9093
        assert settings.kafka_prefix == "custom_"
        assert settings.max_streams == 20

        # Test connection_details with custom values
        details = settings.connection_details
        assert details["kafka_connection"] is True
        assert details["kafka_host"] == "kafka.example.com"
        assert details["kafka_port"] == 9093

    def test_kafka_settings_global_instance(self):
        """Test the global kafka_settings instance."""
        # This should cover the instantiation line
        assert kafka_settings is not None
        assert isinstance(kafka_settings, KafkaSettings)
        assert hasattr(kafka_settings, "kafka_host")
        assert hasattr(kafka_settings, "connection_details")
