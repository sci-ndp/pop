# tests/test_post_general_dataset.py
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from api.models.general_dataset_request_model import GeneralDatasetRequest
from api.routes.register_routes.post_general_dataset import (
    create_general_dataset_endpoint,
)


class TestCreateGeneralDatasetEndpoint:
    """Test cases for create_general_dataset_endpoint."""

    @pytest.fixture
    def sample_dataset_request(self):
        """Sample dataset request for testing."""
        return GeneralDatasetRequest(
            name="test_dataset",
            title="Test Dataset",
            owner_org="test_org",
            notes="Test notes",
            tags=["tag1", "tag2"],
            private=False,
        )

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_local_server_success(
        self,
        mock_get_user,
        mock_create_dataset,
        mock_ckan_settings,
        sample_dataset_request,
    ):
        """Test successful dataset creation with local server."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.return_value = "dataset-123"
        mock_ckan_settings.ckan = MagicMock()

        result = await create_general_dataset_endpoint(
            data=sample_dataset_request, server="local", _={"sub": "user123"}
        )

        assert result == {"id": "dataset-123"}
        mock_create_dataset.assert_called_once()

        # Verify create_general_dataset was called with correct parameters
        call_args = mock_create_dataset.call_args
        assert call_args[1]["name"] == "test_dataset"
        assert call_args[1]["title"] == "Test Dataset"
        assert call_args[1]["owner_org"] == "test_org"
        assert call_args[1]["ckan_instance"] == mock_ckan_settings.ckan

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.validate_preckan_fields")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_pre_ckan_server_success(
        self,
        mock_get_user,
        mock_validate,
        mock_create_dataset,
        mock_ckan_settings,
        sample_dataset_request,
    ):
        """Test successful dataset creation with pre_ckan server."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.return_value = "dataset-456"
        mock_validate.return_value = []  # No missing fields
        mock_ckan_settings.pre_ckan_enabled = True
        mock_ckan_settings.pre_ckan = MagicMock()

        result = await create_general_dataset_endpoint(
            data=sample_dataset_request, server="pre_ckan", _={"sub": "user123"}
        )

        assert result == {"id": "dataset-456"}
        mock_validate.assert_called_once()
        mock_create_dataset.assert_called_once()

        # Verify pre_ckan instance was used
        call_args = mock_create_dataset.call_args
        assert call_args[1]["ckan_instance"] == mock_ckan_settings.pre_ckan

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_pre_ckan_disabled(
        self, mock_get_user, mock_ckan_settings, sample_dataset_request
    ):
        """Test error when pre_ckan is disabled."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_ckan_settings.pre_ckan_enabled = False

        with pytest.raises(HTTPException) as exc_info:
            await create_general_dataset_endpoint(
                data=sample_dataset_request, server="pre_ckan", _={"sub": "user123"}
            )

        assert exc_info.value.status_code == 400
        assert "Pre-CKAN is disabled" in str(exc_info.value.detail)

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.validate_preckan_fields")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_pre_ckan_missing_fields(
        self, mock_get_user, mock_validate, mock_ckan_settings, sample_dataset_request
    ):
        """Test error when pre_ckan has missing required fields."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_validate.return_value = ["field1", "field2"]  # Missing fields
        mock_ckan_settings.pre_ckan_enabled = True

        with pytest.raises(HTTPException) as exc_info:
            await create_general_dataset_endpoint(
                data=sample_dataset_request, server="pre_ckan", _={"sub": "user123"}
            )

        assert exc_info.value.status_code == 400
        assert "Missing required fields" in str(exc_info.value.detail)

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_value_error(
        self,
        mock_get_user,
        mock_create_dataset,
        mock_ckan_settings,
        sample_dataset_request,
    ):
        """Test handling of ValueError from create_general_dataset."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.side_effect = ValueError("Invalid data")
        mock_ckan_settings.ckan = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await create_general_dataset_endpoint(
                data=sample_dataset_request, server="local", _={"sub": "user123"}
            )

        assert exc_info.value.status_code == 400
        assert "Invalid data" in str(exc_info.value.detail)

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_key_error(
        self,
        mock_get_user,
        mock_create_dataset,
        mock_ckan_settings,
        sample_dataset_request,
    ):
        """Test handling of KeyError from create_general_dataset."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.side_effect = KeyError("Reserved key")
        mock_ckan_settings.ckan = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await create_general_dataset_endpoint(
                data=sample_dataset_request, server="local", _={"sub": "user123"}
            )

        assert exc_info.value.status_code == 400
        assert "Reserved key error" in str(exc_info.value.detail)

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_no_scheme_error(
        self,
        mock_get_user,
        mock_create_dataset,
        mock_ckan_settings,
        sample_dataset_request,
    ):
        """Test handling of 'No scheme supplied' error."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.side_effect = Exception("No scheme supplied")
        mock_ckan_settings.ckan = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await create_general_dataset_endpoint(
                data=sample_dataset_request, server="local", _={"sub": "user123"}
            )

        assert exc_info.value.status_code == 400
        assert "Server is not configured or unreachable" in str(exc_info.value.detail)

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_duplicate_name_error(
        self,
        mock_get_user,
        mock_create_dataset,
        mock_ckan_settings,
        sample_dataset_request,
    ):
        """Test handling of duplicate name error."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.side_effect = Exception("That name is already in use")
        mock_ckan_settings.ckan = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await create_general_dataset_endpoint(
                data=sample_dataset_request, server="local", _={"sub": "user123"}
            )

        assert exc_info.value.status_code == 409
        assert "Duplicate Dataset" in str(exc_info.value.detail)

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_duplicate_url_error(
        self,
        mock_get_user,
        mock_create_dataset,
        mock_ckan_settings,
        sample_dataset_request,
    ):
        """Test handling of duplicate URL error."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.side_effect = Exception("That URL is already in use")
        mock_ckan_settings.ckan = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await create_general_dataset_endpoint(
                data=sample_dataset_request, server="local", _={"sub": "user123"}
            )

        assert exc_info.value.status_code == 409
        assert "Duplicate Dataset" in str(exc_info.value.detail)

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_generic_error(
        self,
        mock_get_user,
        mock_create_dataset,
        mock_ckan_settings,
        sample_dataset_request,
    ):
        """Test handling of generic errors."""
        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.side_effect = Exception("Some other error")
        mock_ckan_settings.ckan = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await create_general_dataset_endpoint(
                data=sample_dataset_request, server="local", _={"sub": "user123"}
            )

        assert exc_info.value.status_code == 400
        assert "Error creating dataset: Some other error" in str(exc_info.value.detail)

    @patch("api.routes.register_routes.post_general_dataset.ckan_settings")
    @patch("api.routes.register_routes.post_general_dataset.create_general_dataset")
    @patch("api.routes.register_routes.post_general_dataset.get_current_user")
    @pytest.mark.asyncio
    async def test_create_dataset_with_resources(
        self, mock_get_user, mock_create_dataset, mock_ckan_settings
    ):
        """Test dataset creation with resources."""
        from api.models.general_dataset_request_model import ResourceRequest

        # Create dataset request with resources
        resource = ResourceRequest(
            url="http://example.com/data.csv", name="test_resource", format="CSV"
        )
        dataset_request = GeneralDatasetRequest(
            name="test_with_resources",
            title="Test With Resources",
            owner_org="test_org",
            resources=[resource],
        )

        # Setup mocks
        mock_get_user.return_value = {"sub": "user123"}
        mock_create_dataset.return_value = "dataset-with-resources"
        mock_ckan_settings.ckan = MagicMock()

        result = await create_general_dataset_endpoint(
            data=dataset_request, server="local", _={"sub": "user123"}
        )

        assert result == {"id": "dataset-with-resources"}

        # Verify resources were converted to dictionaries
        call_args = mock_create_dataset.call_args
        resources = call_args[1]["resources"]
        assert len(resources) == 1
        assert isinstance(resources[0], dict)
        assert resources[0]["url"] == "http://example.com/data.csv"
