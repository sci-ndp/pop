# api/config/swagger_settings.py

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    swagger_title: str = "API Documentation"
    swagger_description: str = "This is the API documentation."
    swagger_version: str = "0.6.0"
    public: bool = True
    metrics_endpoint: str = "http://fed-api:80/metrics/"
    use_jupyterlab: bool = False
    jupyter_url: str = "https://jupyter.org/try-jupyter/lab/"
    use_dxspaces: bool = False
    dxspaces_url: str = "http://localhost:8001"

    model_config = {
        "env_file": "./env_variables/.env_swagger",
        "extra": "allow",
    }


swagger_settings = Settings()
