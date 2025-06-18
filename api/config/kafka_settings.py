# api/config/kafka_settings.py

from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    kafka_connection: bool = False
    kafka_host: str = "localhost"
    kafka_port: int = 9092
    kafka_prefix: str = "data_stream_"
    max_streams: int = 10

    @property
    def connection_details(self):
        return {
            "kafka_connection": self.kafka_connection,
            "kafka_host": self.kafka_host,
            "kafka_port": self.kafka_port,
            "kafka_prefix": self.kafka_prefix,
            "max_streams": self.max_streams,
        }

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }


kafka_settings = KafkaSettings()
