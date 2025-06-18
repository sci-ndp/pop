import pytest
from fastapi.testclient import TestClient

from api.config.ckan_settings import ckan_settings
from api.config.keycloak_settings import keycloak_settings
from api.main import app

client = TestClient(app)


@pytest.mark.skipif(
    not ckan_settings.ckan_local_enabled,
    reason="Local CKAN is disabled; skipping Kafka integration tests.",
)
def test_kafka_datasource_registration_and_search():
    """
    Integration test to verify Kafka datasource registration and
    subsequent retrieval via search endpoint.

    Steps:
    1. Check CKAN availability.
    2. Ensure organization exists.
    3. Register a new Kafka datasource.
    4. Search the newly registered datasource to confirm it's available.
    """
    headers = {"Authorization": f"Bearer {keycloak_settings.test_username}"}

    # Step 1: Verify CKAN accessibility
    try:
        health_response = client.get("/organization")
        if health_response.status_code != 200:
            pytest.skip("CKAN local is not accessible; skipping test.")
    except Exception as e:
        print("CKAN health check failed:", str(e))
        pytest.skip("CKAN local is not accessible; skipping test.")

    # Step 2: Ensure organization exists
    org_data = {
        "name": "test_org",
        "title": "Test Organization",
        "description": "Organization for integration testing",
    }
    client.post("/organization", json=org_data, headers=headers)

    # Data for Kafka dataset registration
    kafka_data = {
        "dataset_name": "integration_test_kafka",
        "dataset_title": "Integration Test Kafka",
        "owner_org": "test_org",
        "kafka_topic": "test_integration_topic",
        "kafka_host": "localhost",
        "kafka_port": "9092",
        "dataset_description": "Integration test for Kafka endpoint.",
        "extras": {"integration": "true"},
        "mapping": {"field": "value"},
        "processing": {"key": "value"},
    }

    # Step 3: Register Kafka datasource
    response = client.post("/kafka", json=kafka_data, headers=headers)

    status_code = response.status_code
    response_json = response.json()

    print("Status code:", status_code)
    print("Response JSON:", response_json)

    # Skip the test if SSL or connection error is detected
    detail = response_json.get("detail", "").lower()
    if (
        status_code == 400
        and isinstance(response_json, dict)
        and (
            "certificate verify failed" in detail
            or "connection refused" in detail
            or "max retries exceeded" in detail
        )
    ):
        pytest.skip(
            "CKAN connection error when connecting to remote CKAN. "
            "This is an external issue and not related to the API itself."
        )

    assert response.status_code in (201, 409), "Failed to register Kafka dataset."

    # Step 4: Search for the newly registered dataset
    search_response = client.post(
        "/search",
        json={"dataset_name": "integration_test_kafka", "server": "local"},
    )
    assert search_response.status_code == 200, "Search request failed."

    search_results = search_response.json()

    found_dataset = next(
        (
            dataset
            for dataset in search_results
            if dataset.get("name") == "integration_test_kafka"
        ),
        None,
    )

    assert found_dataset is not None, "Kafka datasource not found in search results."

    # Cleanup after test
    client.delete("/kafka/integration_test_kafka", headers=headers)
    client.delete(f"/organization/{org_data['name']}", headers=headers)
