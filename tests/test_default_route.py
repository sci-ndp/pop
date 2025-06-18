from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_index_route():
    # Mock the 'default_services.index' function as defined in 'api.services'
    with patch("api.services.default_services.index") as mock_index:
        mock_index.return_value = {"message": "Hello, World!"}
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, World!"}
        mock_index.assert_called_once()
