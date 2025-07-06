# api/config/swagger_settings.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the API application.

    All settings can be overridden using environment variables.
    """

    swagger_title: str = "API Documentation"
    swagger_description: str = "This is the API documentation."
    swagger_version: str = "0.7.0"
    is_public: bool = True
    metrics_endpoint: str = "https://federation.ndp.utah.edu/metrics/"
    organization: str = "Unknown Organization"
    use_jupyterlab: bool = False
    jupyter_url: str = "https://jupyter.org/try-jupyter/lab/"
    use_dxspaces: bool = False
    dxspaces_url: str = "http://localhost:8001"
    
    # Endpoint Tracking Configuration
    endpoint_tracking_enabled: bool = True
    endpoint_tracking_api_url: str = "https://api.example.com/endpoint-tracking"
    # Endpoint tracking configuration
    endpoint_tracking_enabled: bool = True

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }


swagger_settings = Settings()
