# tests/test_add_service.py
from unittest.mock import MagicMock, patch

import pytest

from api.services.service_services.add_service import RESERVED_KEYS, add_service


def test_reserved_keys_constant():
    """Test that RESERVED_KEYS constant contains expected keys."""
    expected_keys = {
        "name",
        "title",
        "owner_org",
        "notes",
        "id",
        "resources",
        "collection",
        "service_url",
        "service_type",
        "health_check_url",
        "documentation_url",
    }
    assert RESERVED_KEYS == expected_keys


@patch("api.services.service_services.add_service.ckan_settings")
class TestAddService:
    """Test cases for add_service function."""

    def test_add_service_minimal_parameters(self, mock_ckan_settings):
        """Test add_service with minimal required parameters."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "service-123"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        result = add_service(
            service_name="test_service",
            service_title="Test Service",
            owner_org="services",
            service_url="http://api.example.com",
        )

        assert result == "service-123"
        mock_ckan.action.package_create.assert_called_once()
        mock_ckan.action.resource_create.assert_called_once()

    def test_add_service_all_parameters(self, mock_ckan_settings):
        """Test add_service with all parameters provided."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "service-456"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        result = add_service(
            service_name="full_service",
            service_title="Full Service",
            owner_org="services",
            service_url="http://api.example.com/v1",
            service_type="REST API",
            notes="Complete service with all parameters",
            extras={"version": "1.0", "environment": "production"},
            health_check_url="http://api.example.com/health",
            documentation_url="http://api.example.com/docs",
        )

        assert result == "service-456"

        # Verify package_create call
        package_call = mock_ckan.action.package_create.call_args
        package_data = package_call[1]

        assert package_data["name"] == "full_service"
        assert package_data["title"] == "Full Service"
        assert package_data["owner_org"] == "services"
        assert package_data["notes"] == "Complete service with all parameters"

        # Verify extras
        extras_dict = {extra["key"]: extra["value"] for extra in package_data["extras"]}
        assert extras_dict["service_type"] == "REST API"
        assert extras_dict["health_check_url"] == "http://api.example.com/health"
        assert extras_dict["documentation_url"] == "http://api.example.com/docs"
        assert extras_dict["version"] == "1.0"
        assert extras_dict["environment"] == "production"

        # Verify resource_create call
        resource_call = mock_ckan.action.resource_create.call_args
        resource_data = resource_call[1]

        assert resource_data["package_id"] == "service-456"
        assert resource_data["url"] == "http://api.example.com/v1"
        assert resource_data["name"] == "full_service"
        assert resource_data["format"] == "service"
        assert "Full Service" in resource_data["description"]
        assert "http://api.example.com/v1" in resource_data["description"]

    def test_add_service_custom_ckan_instance(self, mock_ckan_settings):
        """Test add_service with custom CKAN instance."""
        # Setup custom mock
        custom_ckan = MagicMock()
        custom_ckan.action.package_create.return_value = {"id": "custom-789"}
        custom_ckan.action.resource_create.return_value = None

        result = add_service(
            service_name="custom_service",
            service_title="Custom Service",
            owner_org="services",
            service_url="http://custom.example.com",
            ckan_instance=custom_ckan,
        )

        assert result == "custom-789"
        custom_ckan.action.package_create.assert_called_once()
        custom_ckan.action.resource_create.assert_called_once()
        # Default CKAN should not be called
        mock_ckan_settings.ckan.action.package_create.assert_not_called()

    def test_add_service_invalid_owner_org(self, mock_ckan_settings):
        """Test add_service with invalid owner_org."""
        with pytest.raises(ValueError, match="owner_org must be 'services'"):
            add_service(
                service_name="invalid_service",
                service_title="Invalid Service",
                owner_org="wrong_org",
                service_url="http://api.example.com",
            )

    def test_add_service_invalid_extras_type(self, mock_ckan_settings):
        """Test add_service with invalid extras type."""
        with pytest.raises(ValueError, match="Extras must be a dictionary or None"):
            add_service(
                service_name="invalid_extras_service",
                service_title="Invalid Extras Service",
                owner_org="services",
                service_url="http://api.example.com",
                extras="invalid_extras",  # Should be dict or None
            )

    def test_add_service_extras_with_reserved_keys(self, mock_ckan_settings):
        """Test add_service with extras containing reserved keys."""
        with pytest.raises(KeyError, match="Extras contain reserved keys"):
            add_service(
                service_name="reserved_keys_service",
                service_title="Reserved Keys Service",
                owner_org="services",
                service_url="http://api.example.com",
                extras={"name": "reserved", "custom": "allowed"},
            )

    def test_add_service_package_create_error(self, mock_ckan_settings):
        """Test add_service when package creation fails."""
        # Setup mock to raise exception
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.side_effect = Exception(
            "Package creation failed"
        )
        mock_ckan_settings.ckan = mock_ckan

        with pytest.raises(Exception, match="Error creating service package"):
            add_service(
                service_name="failing_service",
                service_title="Failing Service",
                owner_org="services",
                service_url="http://api.example.com",
            )

    def test_add_service_resource_create_error(self, mock_ckan_settings):
        """Test add_service when resource creation fails."""
        # Setup mock where package creation succeeds but resource creation fails
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "service-123"}
        mock_ckan.action.resource_create.side_effect = Exception(
            "Resource creation failed"
        )
        mock_ckan_settings.ckan = mock_ckan

        with pytest.raises(Exception, match="Error creating service resource"):
            add_service(
                service_name="failing_resource_service",
                service_title="Failing Resource Service",
                owner_org="services",
                service_url="http://api.example.com",
            )

    def test_add_service_no_package_id_returned(self, mock_ckan_settings):
        """Test add_service when package creation returns no ID."""
        # Setup mock to return empty dict
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {}  # No ID returned
        mock_ckan_settings.ckan = mock_ckan

        # The actual behavior: KeyError is caught and re-raised as package creation error
        with pytest.raises(Exception, match="Error creating service package"):
            add_service(
                service_name="no_id_service",
                service_title="No ID Service",
                owner_org="services",
                service_url="http://api.example.com",
            )

    def test_add_service_default_notes(self, mock_ckan_settings):
        """Test add_service with default notes when none provided."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "default-notes"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        result = add_service(
            service_name="default_notes_service",
            service_title="Default Notes Service",
            owner_org="services",
            service_url="http://api.example.com",
            # notes not provided, should default
        )

        assert result == "default-notes"

        # Verify default notes were set
        package_call = mock_ckan.action.package_create.call_args
        assert package_call[1]["notes"] == "Service: Default Notes Service"

    def test_add_service_explicit_notes(self, mock_ckan_settings):
        """Test add_service with explicit notes provided."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "explicit-notes"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        result = add_service(
            service_name="explicit_notes_service",
            service_title="Explicit Notes Service",
            owner_org="services",
            service_url="http://api.example.com",
            notes="Custom service description",
        )

        assert result == "explicit-notes"

        # Verify explicit notes were used
        package_call = mock_ckan.action.package_create.call_args
        assert package_call[1]["notes"] == "Custom service description"

    def test_add_service_optional_service_fields(self, mock_ckan_settings):
        """Test add_service with only some optional service fields."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "optional-fields"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        result = add_service(
            service_name="optional_service",
            service_title="Optional Service",
            owner_org="services",
            service_url="http://api.example.com",
            service_type="GraphQL API",
            # health_check_url and documentation_url not provided
        )

        assert result == "optional-fields"

        # Verify only service_type was added to extras
        package_call = mock_ckan.action.package_create.call_args
        extras_dict = {
            extra["key"]: extra["value"] for extra in package_call[1]["extras"]
        }
        assert extras_dict["service_type"] == "GraphQL API"
        assert "health_check_url" not in extras_dict
        assert "documentation_url" not in extras_dict

    def test_add_service_no_extras_at_all(self, mock_ckan_settings):
        """Test add_service with no extras or optional fields."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "no-extras"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        result = add_service(
            service_name="no_extras_service",
            service_title="No Extras Service",
            owner_org="services",
            service_url="http://api.example.com",
            # No optional fields provided
        )

        assert result == "no-extras"

        # Verify no extras section was added
        package_call = mock_ckan.action.package_create.call_args
        assert "extras" not in package_call[1]

    def test_add_service_preserve_user_extras(self, mock_ckan_settings):
        """Test that user extras are preserved when adding service extras."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "preserve-extras"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        result = add_service(
            service_name="preserve_service",
            service_title="Preserve Service",
            owner_org="services",
            service_url="http://api.example.com",
            service_type="REST API",
            extras={"custom_field": "custom_value", "environment": "staging"},
        )

        assert result == "preserve-extras"

        # Verify both user and service extras are present
        package_call = mock_ckan.action.package_create.call_args
        extras_dict = {
            extra["key"]: extra["value"] for extra in package_call[1]["extras"]
        }

        # User extras should be preserved
        assert extras_dict["custom_field"] == "custom_value"
        assert extras_dict["environment"] == "staging"
        # Service extras should be added
        assert extras_dict["service_type"] == "REST API"
