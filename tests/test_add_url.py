# tests/test_add_url.py
import json
from unittest.mock import MagicMock, patch

import pytest

from api.services.url_services.add_url import RESERVED_KEYS, add_url


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
        "url",
        "mapping",
        "processing",
        "file_type",
    }
    assert RESERVED_KEYS == expected_keys


@patch("api.services.url_services.add_url.ckan_settings")
@patch("api.services.url_services.add_url.dxspaces_settings")
class TestAddUrl:
    """Test cases for add_url function."""

    def test_add_url_minimal_parameters(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url with minimal required parameters."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "package-123"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        result = add_url(
            resource_name="test_resource",
            resource_title="Test Resource",
            owner_org="test_org",
            resource_url="http://example.com/data",
        )

        assert result == "package-123"
        mock_ckan.action.package_create.assert_called_once()
        mock_ckan.action.resource_create.assert_called_once()

    def test_add_url_all_parameters(self, mock_dxspaces_settings, mock_ckan_settings):
        """Test add_url with all parameters provided."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "package-456"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        result = add_url(
            resource_name="full_resource",
            resource_title="Full Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.csv",
            file_type="CSV",
            notes="Test resource with all parameters",
            extras={"custom_field": "custom_value"},
            mapping={"field1": "col1"},
            processing={"delimiter": ",", "header_line": "0"},
        )

        assert result == "package-456"

        # Verify package_create call
        package_call = mock_ckan.action.package_create.call_args
        package_data = package_call[1]

        assert package_data["name"] == "full_resource"
        assert package_data["title"] == "Full Resource"
        assert package_data["owner_org"] == "test_org"
        assert package_data["notes"] == "Test resource with all parameters"

        # Verify extras
        extras_dict = {extra["key"]: extra["value"] for extra in package_data["extras"]}
        assert extras_dict["file_type"] == "CSV"
        assert extras_dict["custom_field"] == "custom_value"
        assert '"field1": "col1"' in extras_dict["mapping"]
        assert '"delimiter": ","' in extras_dict["processing"]

        # Verify resource_create call
        resource_call = mock_ckan.action.resource_create.call_args
        resource_data = resource_call[1]

        assert resource_data["package_id"] == "package-456"
        assert resource_data["url"] == "http://example.com/data.csv"
        assert resource_data["name"] == "full_resource"
        assert resource_data["format"] == "url"

    def test_add_url_custom_ckan_instance(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url with custom CKAN instance."""
        # Setup custom mock
        custom_ckan = MagicMock()
        custom_ckan.action.package_create.return_value = {"id": "custom-789"}
        custom_ckan.action.resource_create.return_value = None
        mock_dxspaces_settings.registration_methods = {"url": False}

        result = add_url(
            resource_name="custom_resource",
            resource_title="Custom Resource",
            owner_org="test_org",
            resource_url="http://example.com/data",
            ckan_instance=custom_ckan,
        )

        assert result == "custom-789"
        custom_ckan.action.package_create.assert_called_once()
        custom_ckan.action.resource_create.assert_called_once()
        # Default CKAN should not be called
        mock_ckan_settings.ckan.action.package_create.assert_not_called()

    def test_add_url_netcdf_with_dxspaces(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url with NetCDF file type and dxspaces registration."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "netcdf-123"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        # Setup dxspaces mocks
        mock_dxspaces_settings.registration_methods = {"url": True}
        mock_dxspaces = MagicMock()
        mock_staging_handle = MagicMock()
        mock_staging_handle.model_dump_json.return_value = '{"handle": "staging_123"}'
        mock_dxspaces.Register.return_value = mock_staging_handle
        mock_dxspaces_settings.dxspaces = mock_dxspaces
        mock_dxspaces_settings.dxspaces_url = "http://dxspaces.example.com"

        result = add_url(
            resource_name="netcdf_resource",
            resource_title="NetCDF Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.nc",
            file_type="NetCDF",
        )

        assert result == "netcdf-123"

        # Verify dxspaces registration was called
        mock_dxspaces.Register.assert_called_once_with(
            "url", "netcdf_resource", {"url": "http://example.com/data.nc"}
        )

        # Verify staging extras were added
        package_call = mock_ckan.action.package_create.call_args
        extras_dict = {
            extra["key"]: extra["value"] for extra in package_call[1]["extras"]
        }
        assert extras_dict["staging_socket"] == "http://dxspaces.example.com"
        assert extras_dict["staging_handle"] == '{"handle": "staging_123"}'
        assert extras_dict["file_type"] == "NetCDF"

    def test_add_url_netcdf_with_existing_extras(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url with NetCDF and existing extras."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "netcdf-456"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        # Setup dxspaces mocks
        mock_dxspaces_settings.registration_methods = {"url": True}
        mock_dxspaces = MagicMock()
        mock_staging_handle = MagicMock()
        mock_staging_handle.model_dump_json.return_value = '{"handle": "staging_456"}'
        mock_dxspaces.Register.return_value = mock_staging_handle
        mock_dxspaces_settings.dxspaces = mock_dxspaces
        mock_dxspaces_settings.dxspaces_url = "http://dxspaces.example.com"

        result = add_url(
            resource_name="netcdf_resource_extra",
            resource_title="NetCDF Resource with Extras",
            owner_org="test_org",
            resource_url="http://example.com/data.nc",
            file_type="NetCDF",
            extras={"existing_field": "existing_value"},
        )

        assert result == "netcdf-456"

        # Verify all extras are present
        package_call = mock_ckan.action.package_create.call_args
        extras_dict = {
            extra["key"]: extra["value"] for extra in package_call[1]["extras"]
        }
        assert extras_dict["existing_field"] == "existing_value"
        assert extras_dict["staging_socket"] == "http://dxspaces.example.com"
        assert extras_dict["staging_handle"] == '{"handle": "staging_456"}'
        assert extras_dict["file_type"] == "NetCDF"

    def test_add_url_invalid_extras_type(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url with invalid extras type."""
        mock_dxspaces_settings.registration_methods = {"url": False}

        with pytest.raises(ValueError, match="Extras must be a dictionary or None"):
            add_url(
                resource_name="test_resource",
                resource_title="Test Resource",
                owner_org="test_org",
                resource_url="http://example.com/data",
                extras="invalid_extras",  # Should be dict or None
            )

    def test_add_url_extras_with_reserved_keys(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url with extras containing reserved keys."""
        mock_dxspaces_settings.registration_methods = {"url": False}

        with pytest.raises(KeyError, match="Extras contain reserved keys"):
            add_url(
                resource_name="test_resource",
                resource_title="Test Resource",
                owner_org="test_org",
                resource_url="http://example.com/data",
                extras={"name": "reserved", "custom": "allowed"},
            )

    def test_add_url_package_create_error(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url when package creation fails."""
        # Setup mock to raise exception
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.side_effect = Exception(
            "Package creation failed"
        )
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        with pytest.raises(Exception, match="Error creating resource package"):
            add_url(
                resource_name="failing_resource",
                resource_title="Failing Resource",
                owner_org="test_org",
                resource_url="http://example.com/data",
            )

    def test_add_url_resource_create_error(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url when resource creation fails."""
        # Setup mock where package creation succeeds but resource creation fails
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "package-123"}
        mock_ckan.action.resource_create.side_effect = Exception(
            "Resource creation failed"
        )
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        with pytest.raises(Exception, match="Error creating resource"):
            add_url(
                resource_name="failing_resource",
                resource_title="Failing Resource",
                owner_org="test_org",
                resource_url="http://example.com/data",
            )

    def test_add_url_no_package_id_returned(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test add_url when package creation returns no ID."""
        # Setup mock to return None or empty dict
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {}  # No ID returned
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        # The actual behavior: KeyError is caught and re-raised as package creation error
        with pytest.raises(Exception, match="Error creating resource package"):
            add_url(
                resource_name="no_id_resource",
                resource_title="No ID Resource",
                owner_org="test_org",
                resource_url="http://example.com/data",
            )

    def test_add_url_mapping_and_processing_serialization(
        self, mock_dxspaces_settings, mock_ckan_settings
    ):
        """Test that mapping and processing are properly serialized to JSON."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "json-test"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        mapping_data = {"field1": "col1", "field2": "col2"}
        processing_data = {"delimiter": ",", "header_line": 0, "start_line": 1}

        result = add_url(
            resource_name="json_test",
            resource_title="JSON Test",
            owner_org="test_org",
            resource_url="http://example.com/data.csv",
            mapping=mapping_data,
            processing=processing_data,
        )

        assert result == "json-test"

        # Verify JSON serialization
        package_call = mock_ckan.action.package_create.call_args
        extras_dict = {
            extra["key"]: extra["value"] for extra in package_call[1]["extras"]
        }

        # Verify mapping is serialized
        mapping_json = json.loads(extras_dict["mapping"])
        assert mapping_json == mapping_data

        # Verify processing is serialized
        processing_json = json.loads(extras_dict["processing"])
        assert processing_json == processing_data

    def test_add_url_empty_file_type(self, mock_dxspaces_settings, mock_ckan_settings):
        """Test add_url with empty file_type (default value)."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "empty-file-type"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        result = add_url(
            resource_name="empty_type_resource",
            resource_title="Empty Type Resource",
            owner_org="test_org",
            resource_url="http://example.com/data",
            # file_type defaults to ""
        )

        assert result == "empty-file-type"

        # Verify file_type is empty string in extras
        package_call = mock_ckan.action.package_create.call_args
        extras_dict = {
            extra["key"]: extra["value"] for extra in package_call[1]["extras"]
        }
        assert extras_dict["file_type"] == ""

    def test_add_url_empty_notes(self, mock_dxspaces_settings, mock_ckan_settings):
        """Test add_url with empty notes (default value)."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "empty-notes"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        result = add_url(
            resource_name="empty_notes_resource",
            resource_title="Empty Notes Resource",
            owner_org="test_org",
            resource_url="http://example.com/data",
            # notes defaults to ""
        )

        assert result == "empty-notes"

        # Verify notes is empty string
        package_call = mock_ckan.action.package_create.call_args
        assert package_call[1]["notes"] == ""

    def test_add_url_none_extras(self, mock_dxspaces_settings, mock_ckan_settings):
        """Test add_url with None extras (default value)."""
        # Setup mocks
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "none-extras"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan
        mock_dxspaces_settings.registration_methods = {"url": False}

        result = add_url(
            resource_name="none_extras_resource",
            resource_title="None Extras Resource",
            owner_org="test_org",
            resource_url="http://example.com/data",
            extras=None,  # Explicitly None
        )

        assert result == "none-extras"

        # Verify only file_type extra is present
        package_call = mock_ckan.action.package_create.call_args
        extras_dict = {
            extra["key"]: extra["value"] for extra in package_call[1]["extras"]
        }
        assert len(extras_dict) == 1  # Only file_type
        assert extras_dict["file_type"] == ""
