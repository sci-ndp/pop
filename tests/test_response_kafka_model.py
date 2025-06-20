# tests/test_response_kafka_model.py
from api.models.response_kafka_model import KafkaDataSourceResponse, KafkaResource


class TestKafkaResource:
    """Test cases for KafkaResource model."""

    def test_kafka_resource_creation(self):
        """Test KafkaResource model creation with required fields."""
        resource = KafkaResource(
            id="resource-123",
            kafka_host="localhost",
            kafka_port="9092",
            kafka_topic="test-topic",
        )

        assert resource.id == "resource-123"
        assert resource.kafka_host == "localhost"
        assert resource.kafka_port == "9092"
        assert resource.kafka_topic == "test-topic"
        assert resource.description is None

    def test_kafka_resource_with_description(self):
        """Test KafkaResource with optional description."""
        resource = KafkaResource(
            id="resource-456",
            kafka_host="kafka.example.com",
            kafka_port="9093",
            kafka_topic="sensor-data",
            description="Sensor data from IoT devices",
        )

        assert resource.description == "Sensor data from IoT devices"

    def test_kafka_resource_serialization(self):
        """Test KafkaResource serialization."""
        resource = KafkaResource(
            id="resource-789",
            kafka_host="prod-kafka",
            kafka_port="9094",
            kafka_topic="events",
        )

        resource_dict = resource.model_dump()

        assert resource_dict["id"] == "resource-789"
        assert resource_dict["kafka_host"] == "prod-kafka"
        assert resource_dict["kafka_port"] == "9094"
        assert resource_dict["kafka_topic"] == "events"


class TestKafkaDataSourceResponse:
    """Test cases for KafkaDataSourceResponse model."""

    def test_kafka_datasource_response_minimal(self):
        """Test KafkaDataSourceResponse with minimal required fields."""
        response = KafkaDataSourceResponse(
            id="dataset-123", name="test-dataset", title="Test Dataset", resources=[]
        )

        assert response.id == "dataset-123"
        assert response.name == "test-dataset"
        assert response.title == "Test Dataset"
        assert response.resources == []
        assert response.organization_id is None
        assert response.description is None
        assert response.extras is None

    def test_kafka_datasource_response_complete(self):
        """Test KafkaDataSourceResponse with all fields."""
        kafka_resource = KafkaResource(
            id="res-123",
            kafka_host="kafka.example.com",
            kafka_port="9092",
            kafka_topic="data-stream",
            description="Main data stream",
        )

        response = KafkaDataSourceResponse(
            id="dataset-456",
            name="complete-dataset",
            title="Complete Kafka Dataset",
            organization_id="org-789",
            description="A complete kafka dataset with all fields",
            resources=[kafka_resource],
            extras={"version": "1.0", "environment": "production"},
        )

        assert response.id == "dataset-456"
        assert response.name == "complete-dataset"
        assert response.title == "Complete Kafka Dataset"
        assert response.organization_id == "org-789"
        assert response.description == "A complete kafka dataset with all fields"
        assert len(response.resources) == 1
        assert response.resources[0].kafka_topic == "data-stream"
        assert response.extras == {"version": "1.0", "environment": "production"}

    def test_kafka_datasource_response_aliases(self):
        """Test KafkaDataSourceResponse with field aliases."""
        response = KafkaDataSourceResponse(
            id="alias-test",
            name="alias-dataset",
            title="Alias Test",
            owner_org="alias-org",  # Using alias
            notes="Description via alias",  # Using alias
            resources=[],
        )

        assert response.organization_id == "alias-org"
        assert response.description == "Description via alias"

    def test_kafka_datasource_response_serialization(self):
        """Test KafkaDataSourceResponse serialization."""
        kafka_resource = KafkaResource(
            id="ser-res",
            kafka_host="serialization-kafka",
            kafka_port="9092",
            kafka_topic="serialization-topic",
        )

        response = KafkaDataSourceResponse(
            id="ser-dataset",
            name="serialization-test",
            title="Serialization Test",
            resources=[kafka_resource],
        )

        response_dict = response.model_dump()

        assert response_dict["id"] == "ser-dataset"
        assert response_dict["name"] == "serialization-test"
        assert response_dict["title"] == "Serialization Test"
        assert len(response_dict["resources"]) == 1
        assert response_dict["resources"][0]["kafka_topic"] == "serialization-topic"
