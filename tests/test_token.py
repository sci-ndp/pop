from fastapi.testclient import TestClient

from api.config.keycloak_settings import keycloak_settings
from api.main import app

client = TestClient(app)


def test_login_for_access_token_success():
    response = client.post(
        "/token",
        data={
            "username": keycloak_settings.test_username,
            "password": keycloak_settings.test_password,
        },
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_for_access_token_failure():
    # Test incorrect credentials
    response = client.post(
        "/token", data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
