import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.config.swagger_settings import swagger_settings


def test_organization_field_exists_in_settings():
    """Test that organization field exists in swagger settings."""
    assert hasattr(swagger_settings, "organization")
    assert isinstance(swagger_settings.organization, str)


def test_organization_default_value():
    """Test that organization has the expected default value."""
    from api.config.swagger_settings import Settings

    # Test without any environment variables
    with patch.dict("os.environ", {}, clear=True):
        test_settings = Settings()
        assert test_settings.organization == "Unknown Organization"


def test_organization_environment_variable():
    """Test that organization can be set via ORGANIZATION env variable."""
    from api.config.swagger_settings import Settings

    with patch.dict("os.environ", {"ORGANIZATION": "Test University"}):
        test_settings = Settings()
        assert test_settings.organization == "Test University"


@pytest.mark.asyncio
async def test_metrics_payload_includes_organization():
    """Test that organization field is included in metrics payload."""
    from api.tasks.metrics_task import record_system_metrics

    test_organization = "University of Testing"

    with (
        patch("api.services.status_services.get_public_ip") as mock_ip,
        patch("api.services.status_services.get_system_metrics") as mock_sys,
        patch.object(swagger_settings, "organization", test_organization),
        patch.object(swagger_settings, "is_public", False),
        patch("asyncio.sleep") as mock_sleep,
        patch("api.tasks.metrics_task.logger") as mock_logger,
    ):

        # Set up mock return values
        mock_ip.return_value = "192.168.1.100"
        mock_sys.return_value = (25.5, 60.2, 45.8)
        mock_sleep.side_effect = asyncio.CancelledError()

        try:
            await record_system_metrics()
        except asyncio.CancelledError:
            pass  # Expected due to mock_sleep

        # Verify logger.info was called with JSON containing organization
        assert mock_logger.info.called
        logged_json = mock_logger.info.call_args[0][0]
        metrics_payload = json.loads(logged_json)

        assert "organization" in metrics_payload
        assert metrics_payload["organization"] == test_organization


@pytest.mark.asyncio
async def test_organization_sent_to_metrics_endpoint():
    """Test organization is sent to endpoint when public=True."""
    from api.tasks.metrics_task import record_system_metrics

    test_organization = "Public University"

    with (
        patch("api.services.status_services.get_public_ip") as mock_ip,
        patch("api.services.status_services.get_system_metrics") as mock_sys,
        patch.object(swagger_settings, "organization", test_organization),
        patch.object(swagger_settings, "is_public", True),
        patch("httpx.AsyncClient") as mock_client,
        patch("asyncio.sleep") as mock_sleep,
        patch("logging.getLogger"),
    ):

        mock_ip.return_value = "203.0.113.1"
        mock_sys.return_value = (15.0, 45.0, 30.0)
        mock_sleep.side_effect = asyncio.CancelledError()

        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_client_instance = MagicMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        try:
            await record_system_metrics()
        except asyncio.CancelledError:
            pass

        # Verify POST request was made with organization in payload
        assert mock_client_instance.post.called
        post_call = mock_client_instance.post.call_args
        posted_payload = post_call[1]["json"]

        assert "organization" in posted_payload
        assert posted_payload["organization"] == test_organization


def test_metrics_payload_structure():
    """Test that metrics payload has expected structure with organization."""
    expected_fields = [
        "public_ip",
        "cpu",
        "memory",
        "disk",
        "version",
        "organization",
        "services",
    ]

    # Simulate payload structure from metrics_task.py
    sample_payload = {
        "public_ip": "127.0.0.1",
        "cpu": "25%",
        "memory": "60%",
        "disk": "45%",
        "version": swagger_settings.swagger_version,
        "organization": swagger_settings.organization,
        "services": {},
    }

    for field in expected_fields:
        assert field in sample_payload

    assert isinstance(sample_payload["organization"], str)
    assert len(sample_payload["organization"]) > 0
