# api\config\keycloak_settings.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    keycloak_enabled: bool = True
    keycloak_url: str = "http://localhost:5000"
    realm_name: str = "test"
    client_id: str = "test"
    client_secret: str = "test"
    test_username: str = "test"
    test_password: str = "test"

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }


keycloak_settings = Settings()
