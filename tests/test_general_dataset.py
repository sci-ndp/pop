# tests/test_general_dataset.py
from unittest.mock import MagicMock, patch

import pytest

from api.services.dataset_services.general_dataset import (
    RESERVED_KEYS,
    create_general_dataset,
    patch_general_dataset,
    update_general_dataset,
)


def test_reserved_keys_constant():
    """Test that RESERVED_KEYS constant contains expected keys."""
    expected_keys = {
        "name",
        "title",
        "owner_org",
        "notes",
        "id",
        "resources",
        "tags",
        "private",
        "license_id",
        "version",
        "state",
        "created",
        "last_modified",
        "url",
    }
    assert RESERVED_KEYS == expected_keys


@patch("api.services.dataset_services.general_dataset.ckan_settings")
class TestCreateGeneralDataset:
    """Test cases for create_general_dataset function."""

    def test_create_minimal_dataset(self, mock_ckan_settings):
        """Test creating dataset with minimal required parameters."""
        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "dataset-123"}
        mock_ckan_settings.ckan = mock_ckan

        result = create_general_dataset(
            name="test_dataset", title="Test Dataset", owner_org="test_org"
        )

        assert result == "dataset-123"
        mock_ckan.action.package_create.assert_called_once()

        # Verify the call arguments
        call_args = mock_ckan.action.package_create.call_args[1]
        assert call_args["name"] == "test_dataset"
        assert call_args["title"] == "Test Dataset"
        assert call_args["owner_org"] == "test_org"
        assert call_args["private"] is False

    def test_create_complete_dataset(self, mock_ckan_settings):
        """Test creating dataset with all parameters."""
        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "dataset-456"}
        mock_ckan.action.resource_create.return_value = None
        mock_ckan_settings.ckan = mock_ckan

        result = create_general_dataset(
            name="complete_dataset",
            title="Complete Dataset",
            owner_org="test_org",
            notes="This is a complete dataset",
            tags=["tag1", "tag2"],
            groups=["group1"],
            extras={"custom_field": "custom_value"},
            resources=[{"url": "http://example.com/data.csv", "name": "data"}],
            private=True,
            license_id="mit",
            version="1.0",
        )

        assert result == "dataset-456"

        # Verify package_create call
        package_call = mock_ckan.action.package_create.call_args[1]
        assert package_call["notes"] == "This is a complete dataset"
        assert package_call["private"] is True
        assert package_call["license_id"] == "mit"
        assert package_call["version"] == "1.0"
        assert package_call["tags"] == [{"name": "tag1"}, {"name": "tag2"}]
        assert package_call["groups"] == [{"name": "group1"}]
        assert len(package_call["extras"]) == 1
        assert package_call["extras"][0]["key"] == "custom_field"

        # Verify resource_create was called
        mock_ckan.action.resource_create.assert_called_once()
        resource_call = mock_ckan.action.resource_create.call_args[1]
        assert resource_call["package_id"] == "dataset-456"
        assert resource_call["url"] == "http://example.com/data.csv"

    def test_create_custom_ckan_instance(self, mock_ckan_settings):
        """Test creating dataset with custom CKAN instance."""
        custom_ckan = MagicMock()
        custom_ckan.action.package_create.return_value = {"id": "custom-789"}

        result = create_general_dataset(
            name="custom_dataset",
            title="Custom Dataset",
            owner_org="test_org",
            ckan_instance=custom_ckan,
        )

        assert result == "custom-789"
        custom_ckan.action.package_create.assert_called_once()
        # Default CKAN should not be called
        mock_ckan_settings.ckan.action.package_create.assert_not_called()

    def test_create_invalid_extras_type(self, mock_ckan_settings):
        """Test creating dataset with invalid extras type."""
        with pytest.raises(ValueError, match="Extras must be a dictionary or None"):
            create_general_dataset(
                name="invalid_dataset",
                title="Invalid Dataset",
                owner_org="test_org",
                extras="invalid_extras",
            )

    def test_create_reserved_keys_in_extras(self, mock_ckan_settings):
        """Test creating dataset with reserved keys in extras."""
        with pytest.raises(KeyError, match="Extras contain reserved keys"):
            create_general_dataset(
                name="reserved_dataset",
                title="Reserved Dataset",
                owner_org="test_org",
                extras={"name": "reserved", "custom": "allowed"},
            )

    def test_create_package_creation_error(self, mock_ckan_settings):
        """Test handling package creation errors."""
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.side_effect = Exception(
            "Package creation failed"
        )
        mock_ckan_settings.ckan = mock_ckan

        with pytest.raises(Exception, match="Error creating general dataset"):
            create_general_dataset(
                name="error_dataset", title="Error Dataset", owner_org="test_org"
            )

    def test_create_resource_creation_error(self, mock_ckan_settings):
        """Test handling resource creation errors."""
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "dataset-123"}
        mock_ckan.action.resource_create.side_effect = Exception(
            "Resource creation failed"
        )
        mock_ckan_settings.ckan = mock_ckan

        with pytest.raises(Exception, match="Error creating dataset resources"):
            create_general_dataset(
                name="resource_error_dataset",
                title="Resource Error Dataset",
                owner_org="test_org",
                resources=[{"url": "http://example.com/data.csv"}],
            )

    def test_create_without_optional_fields(self, mock_ckan_settings):
        """Test creating dataset without optional fields."""
        mock_ckan = MagicMock()
        mock_ckan.action.package_create.return_value = {"id": "minimal-123"}
        mock_ckan_settings.ckan = mock_ckan

        result = create_general_dataset(
            name="minimal_dataset",
            title="Minimal Dataset",
            owner_org="test_org",
            # No optional fields provided
        )

        assert result == "minimal-123"

        # Verify only required fields are in the call
        call_args = mock_ckan.action.package_create.call_args[1]
        assert "notes" not in call_args
        assert "license_id" not in call_args
        assert "version" not in call_args
        assert "tags" not in call_args
        assert "groups" not in call_args
        assert "extras" not in call_args


@patch("api.services.dataset_services.general_dataset.ckan_settings")
class TestUpdateGeneralDataset:
    """Test cases for update_general_dataset function."""

    @pytest.fixture
    def sample_existing_dataset(self):
        """Sample existing dataset for update tests."""
        return {
            "id": "existing-123",
            "name": "existing_dataset",
            "title": "Existing Dataset",
            "owner_org": "existing_org",
            "notes": "Existing notes",
            "private": False,
            "extras": [{"key": "existing_key", "value": "existing_value"}],
        }

    def test_update_dataset_minimal(self, mock_ckan_settings, sample_existing_dataset):
        """Test updating dataset with minimal parameters."""
        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_existing_dataset
        mock_ckan.action.package_update.return_value = {"id": "existing-123"}
        mock_ckan_settings.ckan = mock_ckan

        result = update_general_dataset(
            dataset_id="existing-123", title="Updated Title"
        )

        assert result == "existing-123"
        mock_ckan.action.package_show.assert_called_once_with(id="existing-123")
        mock_ckan.action.package_update.assert_called_once()

        # Verify the update preserved existing values and updated title
        update_call = mock_ckan.action.package_update.call_args[1]
        assert update_call["title"] == "Updated Title"
        assert update_call["name"] == "existing_dataset"  # Preserved

    def test_update_dataset_complete(self, mock_ckan_settings, sample_existing_dataset):
        """Test updating dataset with all parameters."""
        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_existing_dataset
        mock_ckan.action.package_update.return_value = {"id": "existing-123"}
        mock_ckan_settings.ckan = mock_ckan

        result = update_general_dataset(
            dataset_id="existing-123",
            name="updated_dataset",
            title="Updated Dataset",
            owner_org="updated_org",
            notes="Updated notes",
            tags=["new_tag"],
            groups=["new_group"],
            extras={"new_key": "new_value"},
            private=True,
            license_id="gpl",
            version="2.0",
        )

        assert result == "existing-123"

        # Verify all fields were updated
        update_call = mock_ckan.action.package_update.call_args[1]
        assert update_call["name"] == "updated_dataset"
        assert update_call["title"] == "Updated Dataset"
        assert update_call["owner_org"] == "updated_org"
        assert update_call["notes"] == "Updated notes"
        assert update_call["private"] is True
        assert update_call["license_id"] == "gpl"
        assert update_call["version"] == "2.0"
        assert update_call["tags"] == [{"name": "new_tag"}]
        assert update_call["groups"] == [{"name": "new_group"}]

        # Verify extras were merged
        extras_dict = {extra["key"]: extra["value"] for extra in update_call["extras"]}
        assert extras_dict["existing_key"] == "existing_value"  # Preserved
        assert extras_dict["new_key"] == "new_value"  # Added

    def test_update_fetch_error(self, mock_ckan_settings):
        """Test handling errors when fetching dataset for update."""
        mock_ckan = MagicMock()
        mock_ckan.action.package_show.side_effect = Exception("Dataset not found")
        mock_ckan_settings.ckan = mock_ckan

        with pytest.raises(Exception, match="Error fetching dataset"):
            update_general_dataset(dataset_id="nonexistent-123")

    def test_update_package_update_error(
        self, mock_ckan_settings, sample_existing_dataset
    ):
        """Test handling errors during package update."""
        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = sample_existing_dataset
        mock_ckan.action.package_update.side_effect = Exception("Update failed")
        mock_ckan_settings.ckan = mock_ckan

        with pytest.raises(Exception, match="Error updating general dataset"):
            update_general_dataset(dataset_id="existing-123", title="Updated Title")

    def test_update_invalid_extras(self, mock_ckan_settings):
        """Test updating with invalid extras."""
        with pytest.raises(ValueError, match="Extras must be a dictionary or None"):
            update_general_dataset(dataset_id="existing-123", extras="invalid_extras")

    def test_update_reserved_keys_in_extras(self, mock_ckan_settings):
        """Test updating with reserved keys in extras."""
        with pytest.raises(KeyError, match="Extras contain reserved keys"):
            update_general_dataset(
                dataset_id="existing-123",
                extras={"id": "reserved", "custom": "allowed"},
            )


@patch("api.services.dataset_services.general_dataset.ckan_settings")
class TestPatchGeneralDataset:
    """Test cases for patch_general_dataset function."""

    def test_patch_dataset(self, mock_ckan_settings):
        """Test patch_general_dataset delegates to update_general_dataset."""
        mock_ckan = MagicMock()
        mock_ckan.action.package_show.return_value = {
            "id": "patch-123",
            "name": "patch_dataset",
            "title": "Patch Dataset",
            "owner_org": "patch_org",
        }
        mock_ckan.action.package_update.return_value = {"id": "patch-123"}
        mock_ckan_settings.ckan = mock_ckan

        # Patch should work exactly like update
        result = patch_general_dataset(dataset_id="patch-123", title="Patched Title")

        assert result == "patch-123"
        mock_ckan.action.package_show.assert_called_once()
        mock_ckan.action.package_update.assert_called_once()

    def test_patch_with_custom_ckan_instance(self, mock_ckan_settings):
        """Test patch with custom CKAN instance."""
        custom_ckan = MagicMock()
        custom_ckan.action.package_show.return_value = {
            "id": "custom-patch-123",
            "name": "custom_patch_dataset",
            "title": "Custom Patch Dataset",
            "owner_org": "custom_org",
        }
        custom_ckan.action.package_update.return_value = {"id": "custom-patch-123"}

        result = patch_general_dataset(
            dataset_id="custom-patch-123",
            title="Custom Patched Title",
            ckan_instance=custom_ckan,
        )

        assert result == "custom-patch-123"
        custom_ckan.action.package_show.assert_called_once()
        custom_ckan.action.package_update.assert_called_once()
        # Default CKAN should not be called
        mock_ckan_settings.ckan.action.package_show.assert_not_called()
