# api/models/endpoint_tracking_model.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EndpointTrackingRequest(BaseModel):
    """Model for endpoint tracking data."""

    endpoint: str = Field(
        ...,
        description="The endpoint path that was accessed",
        json_schema_extra={"example": "/api/v1/organization"}
    )
    method: str = Field(
        ...,
        description="HTTP method used (GET, POST, PUT, DELETE, etc.)",
        json_schema_extra={"example": "POST"}
    )
    client_id: str = Field(
        ...,
        description="Client ID from environment configuration",
        json_schema_extra={"example": "saleem_test"}
    )
    organization: str = Field(
        ...,
        description="Organization name from environment configuration",
        json_schema_extra={"example": "SCI - University of Utah"}
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the endpoint was accessed",
        json_schema_extra={"example": "2025-01-15T10:30:00Z"}
    )
    user_agent: Optional[str] = Field(
        None,
        description="User agent string from the request",
        json_schema_extra={"example": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."}
    )
    remote_addr: Optional[str] = Field(
        None,
        description="Remote IP address of the client",
        json_schema_extra={"example": "192.168.1.100"}
    )
    status_code: Optional[int] = Field(
        None,
        description="HTTP status code of the response",
        json_schema_extra={"example": 200}
    )
    request_data: Optional[dict] = Field(
        None,
        description="Key request parameters and data (for successful requests only)",
        json_schema_extra={"example": {"search_term": "climate data", "organization_name": "research_org"}}
    )
    query_params: Optional[dict] = Field(
        None,
        description="URL query parameters",
        json_schema_extra={"example": {"server": "local", "limit": "10"}}
    )
