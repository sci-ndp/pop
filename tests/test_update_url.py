# tests/test_update_url.py
from unittest.mock import MagicMock, patch

import pytest

from api.services.url_services.update_url import (
    RESERVED_KEYS,
    update_url,
    validate_manual_processing_info,
)


class TestValidateManualProcessingInfo:
    """Test cases for validate_manual_processing_info function."""

    def test_validate_stream_processing_valid(self):
        """Test valid stream processing validation."""
        processing = {"refresh_rate": "10s", "data_key": "data"}
        result = validate_manual_processing_info("stream", processing)
        assert result == processing

    def test_validate_stream_processing_extra_fields(self):
        """Test stream processing with extra fields."""
        processing = {"refresh_rate": "10s", "data_key": "data", "extra": "field"}
        with pytest.raises(ValueError, match="Unexpected fields in processing"):
            validate_manual_processing_info("stream", processing)

    def test_validate_csv_processing_valid(self):
        """Test valid CSV processing validation."""
        processing = {
            "delimiter": ",",
            "header_line": "0",
            "start_line": "1",
            "comment_char": "#",
        }
        result = validate_manual_processing_info("CSV", processing)
        assert result == processing

    def test_validate_csv_processing_minimal_required(self):
        """Test CSV processing with minimal required fields."""
        processing = {"delimiter": ",", "header_line": "0", "start_line": "1"}
        result = validate_manual_processing_info("CSV", processing)
        assert result == processing

    def test_validate_csv_processing_missing_required(self):
        """Test CSV processing missing required fields."""
        processing = {"delimiter": ","}
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_manual_processing_info("CSV", processing)

    def test_validate_txt_processing_valid(self):
        """Test valid TXT processing validation."""
        processing = {"delimiter": "\t", "header_line": "0", "start_line": "1"}
        result = validate_manual_processing_info("TXT", processing)
        assert result == processing

    def test_validate_txt_processing_missing_required(self):
        """Test TXT processing missing required fields."""
        processing = {"delimiter": "\t", "header_line": "0"}
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_manual_processing_info("TXT", processing)

    def test_validate_json_processing_valid(self):
        """Test valid JSON processing validation."""
        processing = {
            "info_key": "metadata",
            "additional_key": "extra",
            "data_key": "data",
        }
        result = validate_manual_processing_info("JSON", processing)
        assert result == processing

    def test_validate_netcdf_processing_valid(self):
        """Test valid NetCDF processing validation."""
        processing = {"group": "main_group"}
        result = validate_manual_processing_info("NetCDF", processing)
        assert result == processing

    def test_validate_unknown_file_type(self):
        """Test processing validation for unknown file type."""
        processing = {"some_field": "value"}
        # Unknown file types should raise error for unexpected fields
        with pytest.raises(ValueError, match="Unexpected fields in processing"):
            validate_manual_processing_info("UNKNOWN", processing)

    def test_validate_unknown_file_type_empty(self):
        """Test processing validation for unknown file type with empty processing."""
        processing = {}
        # Should work for unknown file types with empty processing
        result = validate_manual_processing_info("UNKNOWN", processing)
        assert result == processing

    def test_validate_empty_processing(self):
        """Test processing validation with empty processing dict."""
        processing = {}
        # Should work for file types without required fields
        result = validate_manual_processing_info("JSON", processing)
        assert result == processing

        # Should fail for file types with required fields
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_manual_processing_info("CSV", processing)


@patch("api.services.url_services.update_url.ckan_settings")
class TestUpdateUrl:
    """Test cases for update_url function."""

    @pytest.fixture
    def sample_resource(self):
        """Sample resource data for testing."""
        return {
            "id": "resource-123",
            "name": "test_resource",
            "title": "Test Resource",
            "owner_org": "test_org",
            "notes": "Test resource description",
            "resources": [
                {
                    "id": "url-resource-456",
                    "format": "URL",
                    "url": "http://example.com/data",
                }
            ],
            "extras": [
                {"key": "file_type", "value": "CSV"},
                {
                    "key": "processing",
                    "value": '{"delimiter": ",", "header_line": "0", "start_line": "1"}',
                },
                {"key": "mapping", "value": '{"field1": "col1"}'},
                {"key": "custom_field", "value": "custom_value"},
            ],
        }

    def test_update_url_default_ckan_instance(
        self, mock_ckan_settings, sample_resource
    ):
        """Test update_url with default CKAN instance."""
        import asyncio

        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan.action.package_update.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            result = await update_url(
                resource_id="resource-123", resource_name="updated_resource"
            )

            mock_ckan.action.package_show.assert_called_once_with(id="resource-123")
            mock_ckan.action.package_update.assert_called_once()
            assert result["message"] == "Resource updated successfully"

        asyncio.run(run_test())

    def test_update_url_custom_ckan_instance(self, mock_ckan_settings, sample_resource):
        """Test update_url with custom CKAN instance."""
        import asyncio

        # Setup custom mock
        custom_ckan = MagicMock()
        custom_ckan.action.package_show.return_value = sample_resource
        custom_ckan.action.package_update.return_value = None

        async def run_test():
            result = await update_url(
                resource_id="resource-123",
                resource_name="updated_resource",
                ckan_instance=custom_ckan,
            )

            custom_ckan.action.package_show.assert_called_once_with(id="resource-123")
            custom_ckan.action.package_update.assert_called_once()
            assert result["message"] == "Resource updated successfully"

        asyncio.run(run_test())

    def test_update_url_fetch_error(self, mock_ckan_settings):
        """Test update_url when fetching resource fails."""
        import asyncio

        # Setup mock to raise exception
        mock_ckan = MagicMock()
        mock_ckan.action.package_show.side_effect = Exception("Resource not found")
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            with pytest.raises(
                Exception, match="Error fetching resource with ID resource-123"
            ):
                await update_url(resource_id="resource-123")

        asyncio.run(run_test())

    def test_update_url_all_parameters(self, mock_ckan_settings, sample_resource):
        """Test update_url with all parameters provided."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan.action.package_update.return_value = None
        mock_ckan.action.resource_update.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            result = await update_url(
                resource_id="resource-123",
                resource_name="new_name",
                resource_title="New Title",
                owner_org="new_org",
                resource_url="http://newexample.com/data",
                file_type="JSON",
                notes="New description",
                extras={"new_field": "new_value"},
                mapping={"field2": "col2"},
                processing={"info_key": "metadata"},
            )

            # Verify package_update was called
            mock_ckan.action.package_update.assert_called_once()
            call_args = mock_ckan.action.package_update.call_args

            # Check that the updated data contains our changes
            updated_data = call_args[1]
            assert updated_data["name"] == "new_name"
            assert updated_data["title"] == "New Title"
            assert updated_data["owner_org"] == "new_org"
            assert updated_data["notes"] == "New description"

            # Verify resource_update was called for URL change
            mock_ckan.action.resource_update.assert_called_once_with(
                id="url-resource-456",
                url="http://newexample.com/data",
                package_id="resource-123",
            )

            assert result["message"] == "Resource updated successfully"

        asyncio.run(run_test())

    def test_update_url_file_type_change_with_processing(
        self, mock_ckan_settings, sample_resource
    ):
        """Test update_url when file type changes and processing is provided."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan.action.package_update.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            result = await update_url(
                resource_id="resource-123",
                file_type="JSON",
                processing={"info_key": "metadata", "data_key": "data"},
            )

            mock_ckan.action.package_update.assert_called_once()
            assert result["message"] == "Resource updated successfully"

        asyncio.run(run_test())

    def test_update_url_file_type_change_without_processing(
        self, mock_ckan_settings, sample_resource
    ):
        """Test update_url when file type changes without new processing."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan.action.package_update.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            # This should validate current processing against new file type
            # Current processing is CSV format, new file type is JSON
            # This should raise an error due to incompatible processing
            with pytest.raises(ValueError):
                await update_url(
                    resource_id="resource-123",
                    file_type="JSON",  # Incompatible with current CSV processing
                )

        asyncio.run(run_test())

    def test_update_url_processing_update_only(
        self, mock_ckan_settings, sample_resource
    ):
        """Test update_url when only processing is updated."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan.action.package_update.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            result = await update_url(
                resource_id="resource-123",
                processing={"delimiter": ";", "header_line": "0", "start_line": "1"},
            )

            mock_ckan.action.package_update.assert_called_once()
            assert result["message"] == "Resource updated successfully"

        asyncio.run(run_test())

    def test_update_url_extras_with_reserved_keys(
        self, mock_ckan_settings, sample_resource
    ):
        """Test update_url when extras contain reserved keys."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            with pytest.raises(KeyError, match="Extras contain reserved keys"):
                await update_url(
                    resource_id="resource-123",
                    extras={"name": "reserved", "custom": "allowed"},
                )

        asyncio.run(run_test())

    def test_update_url_no_url_resource(self, mock_ckan_settings):
        """Test update_url when resource has no URL format resource."""
        import asyncio

        # Resource without URL format
        resource_no_url = {
            "id": "resource-123",
            "name": "test_resource",
            "title": "Test Resource",
            "owner_org": "test_org",
            "notes": "Test resource description",
            "resources": [
                {
                    "id": "file-resource-456",
                    "format": "CSV",
                    "url": "http://example.com/data.csv",
                }
            ],
            "extras": [],
        }

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = resource_no_url
        mock_ckan.action.package_update.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            result = await update_url(
                resource_id="resource-123",
                resource_url="http://newexample.com/data",
                resource_name="updated_name",
            )

            # Should update package but not call resource_update
            mock_ckan.action.package_update.assert_called_once()
            mock_ckan.action.resource_update.assert_not_called()
            assert result["message"] == "Resource updated successfully"

        asyncio.run(run_test())

    def test_update_url_package_update_error(self, mock_ckan_settings, sample_resource):
        """Test update_url when package update fails."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan.action.package_update.side_effect = Exception("Update failed")
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            with pytest.raises(
                Exception, match="Error updating resource with ID resource-123"
            ):
                await update_url(
                    resource_id="resource-123", resource_name="updated_name"
                )

        asyncio.run(run_test())

    def test_update_url_partial_updates(self, mock_ckan_settings, sample_resource):
        """Test update_url with partial field updates."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan.action.package_update.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            # Only update title and notes
            result = await update_url(
                resource_id="resource-123",
                resource_title="Updated Title Only",
                notes="Updated notes only",
            )

            mock_ckan.action.package_update.assert_called_once()
            call_args = mock_ckan.action.package_update.call_args
            updated_data = call_args[1]

            # Should preserve original name and owner_org
            assert updated_data["name"] == "test_resource"
            assert updated_data["owner_org"] == "test_org"
            # Should update title and notes
            assert updated_data["title"] == "Updated Title Only"
            assert updated_data["notes"] == "Updated notes only"

            assert result["message"] == "Resource updated successfully"

        asyncio.run(run_test())

    def test_update_url_preserve_existing_extras(
        self, mock_ckan_settings, sample_resource
    ):
        """Test that existing extras are preserved when adding new ones."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_resource
        mock_ckan.action.package_update.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        async def run_test():
            result = await update_url(
                resource_id="resource-123", extras={"new_extra": "new_value"}
            )

            mock_ckan.action.package_update.assert_called_once()
            call_args = mock_ckan.action.package_update.call_args
            updated_data = call_args[1]

            # Extract extras for easier checking
            extras_dict = {
                extra["key"]: extra["value"] for extra in updated_data["extras"]
            }

            # Should preserve existing extras
            assert "file_type" in extras_dict
            assert "processing" in extras_dict
            assert "mapping" in extras_dict
            assert "custom_field" in extras_dict
            # Should add new extra
            assert extras_dict["new_extra"] == "new_value"

            assert result["message"] == "Resource updated successfully"

        asyncio.run(run_test())


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
