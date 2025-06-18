# api/models/service_request_model.py
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class ServiceRequest(BaseModel):
    """
    Request model for service registration.

    All services must be registered under the "services" organization.
    """

    service_name: str = Field(
        ..., description="Unique name for the service", min_length=1, max_length=100
    )
    service_title: str = Field(
        ..., description="Display title for the service", min_length=1, max_length=200
    )
    owner_org: str = Field(
        ..., description="Organization ID (must be 'services')", pattern="^services$"
    )
    service_url: str = Field(..., description="URL where the service is accessible")
    service_type: Optional[str] = Field(
        None,
        description="Type of service (e.g., API, Web Service, Microservice)",
        max_length=50,
    )
    notes: Optional[str] = Field(
        None, description="Additional description or notes about the service"
    )
    extras: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata as key-value pairs"
    )
    health_check_url: Optional[str] = Field(
        None, description="URL for service health check endpoint"
    )
    documentation_url: Optional[str] = Field(
        None, description="URL to service documentation"
    )

    @validator("owner_org")
    def validate_owner_org(cls, v):
        """
        Validate that owner_org is always 'services'.

        Parameters
        ----------
        v : str
            The owner_org value to validate.

        Returns
        -------
        str
            The validated owner_org value.

        Raises
        ------
        ValueError
            If owner_org is not 'services'.
        """
        if v != "services":
            raise ValueError("owner_org must be 'services' for service registration")
        return v

    @validator("service_url", "health_check_url", "documentation_url")
    def validate_urls(cls, v):
        """
        Validate URL format for service-related URLs.

        Parameters
        ----------
        v : str or None
            The URL value to validate.

        Returns
        -------
        str or None
            The validated URL value.

        Raises
        ------
        ValueError
            If URL format is invalid.
        """
        if v is None:
            return v
        if not v.startswith(("http://", "https://")):
            raise ValueError("URLs must start with http:// or https://")
        return v

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "service_name": "user_authentication_api",
                "service_title": "User Authentication API",
                "owner_org": "services",
                "service_url": "https://api.example.com/auth",
                "service_type": "API",
                "notes": "RESTful API for user authentication and authorization",
                "extras": {"version": "2.1.0", "environment": "production"},
                "health_check_url": "https://api.example.com/auth/health",
                "documentation_url": "https://docs.example.com/auth-api",
            }
        }
