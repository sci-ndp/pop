# api/models/system_metrics_model.py

from typing import Optional

from pydantic import BaseModel, Field


class SystemMetrics(BaseModel):
    """Model for system metrics logging."""

    public_ip: str = Field(
        ...,
        description="Public IP address of the machine running the API.",
        json_schema_extra={"example": "192.0.2.1"},
    )
    cpu_usage_percent: float = Field(
        ..., description="CPU usage percentage.", json_schema_extra={"example": 55.5}
    )
    memory_usage_percent: float = Field(
        ..., description="Memory usage percentage.", json_schema_extra={"example": 62.3}
    )
    disk_usage_percent: float = Field(
        ..., description="Disk usage percentage.", json_schema_extra={"example": 74.8}
    )
    timestamp: Optional[str] = Field(
        None,
        description="Timestamp when metrics were collected (ISO 8601).",
        json_schema_extra={"example": "2025-03-13T23:00:00Z"},
    )
