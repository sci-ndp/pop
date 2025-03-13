# api/config/swagger_settings.py

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    swagger_title: str = "API Documentation"
    swagger_description: str = "This is the API documentation."
    swagger_version: str = Field("0.6.0", exclude=True)
    public: bool = True
    use_jupyterlab: bool = False
    jupyter_url: str = "https://jupyter.org/try-jupyter/lab/"

    model_config = {
        "env_file": "./env_variables/.env_swagger",
        "extra": "allow",
    }


swagger_settings = Settings()
