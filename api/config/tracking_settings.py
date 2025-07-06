# api/config/tracking_settings.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for endpoint tracking.
    
    All settings can be overridden using environment variables.
    """
    
    endpoint_tracking_enabled: bool = True
    endpoint_tracking_api_url: str = "https://api.example.com/endpoint-tracking"
    
    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }


tracking_settings = Settings()
