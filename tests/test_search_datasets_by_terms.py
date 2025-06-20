# tests/test_search_datasets_by_terms.py
from unittest.mock import MagicMock, patch

import pytest
from ckanapi import CKANAPIError, NotFound
from fastapi import HTTPException

from api.services.datasource_services.search_datasets_by_terms import (
    escape_solr_special_chars,
    search_datasets_by_terms,
)


class TestEscapeSolrSpecialChars:
    """Test cases for escape_solr_special_chars function."""

    def test_escape_plus_sign(self):
        """Test escaping plus sign."""
        result = escape_solr_special_chars("term+with+plus")
        assert result == "term\\+with\\+plus"

    def test_escape_minus_sign(self):
        """Test escaping minus sign."""
        result = escape_solr_special_chars("term-with-minus")
        assert result == "term\\-with\\-minus"

    def test_escape_exclamation(self):
        """Test escaping exclamation mark."""
        result = escape_solr_special_chars("term!with!exclamation")
        assert result == "term\\!with\\!exclamation"

    def test_escape_parentheses(self):
        """Test escaping parentheses."""
        result = escape_solr_special_chars("term(with)parentheses")
        assert result == "term\\(with\\)parentheses"

    def test_escape_braces(self):
        """Test escaping curly braces."""
        result = escape_solr_special_chars("term{with}braces")
        assert result == "term\\{with\\}braces"

    def test_escape_brackets(self):
        """Test escaping square brackets."""
        result = escape_solr_special_chars("term[with]brackets")
        assert result == "term\\[with\\]brackets"

    def test_escape_caret(self):
        """Test escaping caret."""
        result = escape_solr_special_chars("term^with^caret")
        assert result == "term\\^with\\^caret"

    def test_escape_quotes(self):
        """Test escaping quotes."""
        result = escape_solr_special_chars('term"with"quotes')
        assert result == 'term\\"with\\"quotes'

    def test_escape_tilde(self):
        """Test escaping tilde."""
        result = escape_solr_special_chars("term~with~tilde")
        assert result == "term\\~with\\~tilde"

    def test_escape_asterisk(self):
        """Test escaping asterisk."""
        result = escape_solr_special_chars("term*with*asterisk")
        assert result == "term\\*with\\*asterisk"

    def test_escape_question(self):
        """Test escaping question mark."""
        result = escape_solr_special_chars("term?with?question")
        assert result == "term\\?with\\?question"

    def test_escape_colon(self):
        """Test escaping colon."""
        result = escape_solr_special_chars("term:with:colon")
        assert result == "term\\:with\\:colon"

    def test_escape_backslash(self):
        """Test escaping backslash."""
        result = escape_solr_special_chars("term\\with\\backslash")
        assert result == "term\\\\with\\\\backslash"

    def test_escape_multiple_chars(self):
        """Test escaping multiple special characters."""
        result = escape_solr_special_chars("term+with-multiple*chars!")
        assert result == "term\\+with\\-multiple\\*chars\\!"

    def test_escape_no_special_chars(self):
        """Test string with no special characters."""
        result = escape_solr_special_chars("normalterm")
        assert result == "normalterm"

    def test_escape_empty_string(self):
        """Test empty string."""
        result = escape_solr_special_chars("")
        assert result == ""


@patch("api.services.datasource_services.search_datasets_by_terms.ckan_settings")
class TestSearchDatasetsByTerms:
    """Test cases for search_datasets_by_terms function."""

    @pytest.fixture
    def sample_dataset_response(self):
        """Sample dataset response for testing."""
        return {
            "results": [
                {
                    "id": "dataset-1",
                    "name": "test_dataset",
                    "title": "Test Dataset",
                    "notes": "A test dataset for testing",
                    "organization": {"name": "test_org"},
                    "resources": [
                        {
                            "id": "resource-1",
                            "url": "http://example.com/data.csv",
                            "name": "test_resource",
                            "description": "Test resource",
                            "format": "CSV",
                        }
                    ],
                    "extras": [
                        {"key": "mapping", "value": '{"field1": "value1"}'},
                        {"key": "processing", "value": '{"method": "batch"}'},
                        {"key": "other", "value": "test_value"},
                    ],
                }
            ]
        }

    def test_invalid_server(self, mock_ckan_settings):
        """Test that invalid server raises HTTPException."""
        import asyncio

        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await search_datasets_by_terms(["test"], server="invalid")
            assert exc_info.value.status_code == 400
            assert "Invalid server specified" in str(exc_info.value.detail)

        asyncio.run(run_test())

    def test_local_server_selection(self, mock_ckan_settings, sample_dataset_response):
        """Test local server selection."""
        import asyncio

        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = sample_dataset_response
        mock_ckan_settings.ckan_no_api_key = mock_ckan

        async def run_test():
            result = await search_datasets_by_terms(["test"], server="local")
            mock_ckan.action.package_search.assert_called_once()
            assert len(result) == 1
            assert result[0].name == "test_dataset"

        asyncio.run(run_test())

    def test_global_server_selection(self, mock_ckan_settings, sample_dataset_response):
        """Test global server selection."""
        import asyncio

        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = sample_dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            result = await search_datasets_by_terms(["test"], server="global")
            mock_ckan.action.package_search.assert_called_once()
            assert len(result) == 1

        asyncio.run(run_test())

    def test_pre_ckan_server_selection(
        self, mock_ckan_settings, sample_dataset_response
    ):
        """Test pre_ckan server selection."""
        import asyncio

        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = sample_dataset_response
        mock_ckan_settings.pre_ckan_no_api_key = mock_ckan

        async def run_test():
            result = await search_datasets_by_terms(["test"], server="pre_ckan")
            mock_ckan.action.package_search.assert_called_once()
            assert len(result) == 1

        asyncio.run(run_test())

    def test_search_with_keys_list(self, mock_ckan_settings, sample_dataset_response):
        """Test search with keys list."""
        import asyncio

        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = sample_dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            await search_datasets_by_terms(
                ["test_value", "dataset"], keys_list=["title", "name"], server="global"
            )

            call_args = mock_ckan.action.package_search.call_args
            query = call_args[1]["q"]
            # Keys are escaped but terms are not, and colon is escaped in keys
            assert "title:test_value" in query
            assert "name:dataset" in query
            assert " AND " in query

        asyncio.run(run_test())

    def test_search_with_null_keys(self, mock_ckan_settings, sample_dataset_response):
        """Test search with null keys in keys_list."""
        import asyncio

        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = sample_dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            await search_datasets_by_terms(
                ["test", "dataset"], keys_list=[None, "title"], server="global"
            )

            call_args = mock_ckan.action.package_search.call_args
            query = call_args[1]["q"]
            assert "test AND title:dataset" in query

        asyncio.run(run_test())

    def test_search_with_null_string_keys(
        self, mock_ckan_settings, sample_dataset_response
    ):
        """Test search with 'null' string keys in keys_list."""
        import asyncio

        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = sample_dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            await search_datasets_by_terms(
                ["test", "dataset"], keys_list=["null", "title"], server="global"
            )

            call_args = mock_ckan.action.package_search.call_args
            query = call_args[1]["q"]
            assert "test AND title:dataset" in query

        asyncio.run(run_test())

    def test_search_without_keys_list(
        self, mock_ckan_settings, sample_dataset_response
    ):
        """Test search without keys list."""
        import asyncio

        # Setup mock
        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = sample_dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            await search_datasets_by_terms(["test", "dataset"], server="global")

            call_args = mock_ckan.action.package_search.call_args
            query = call_args[1]["q"]
            assert query == "test AND dataset"

        asyncio.run(run_test())

    def test_term_filtering_case_insensitive(self, mock_ckan_settings):
        """Test that term filtering is case insensitive."""
        import asyncio

        # Setup mock with dataset that should match
        dataset_response = {
            "results": [
                {
                    "id": "dataset-1",
                    "name": "TEST_DATASET",
                    "title": "Test Dataset",
                    "notes": "A test dataset",
                    "organization": {"name": "test_org"},
                    "resources": [],
                    "extras": [],
                }
            ]
        }

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            # Search with lowercase terms, should match uppercase dataset
            result = await search_datasets_by_terms(
                ["test", "dataset"], server="global"
            )
            assert len(result) == 1
            assert result[0].name == "TEST_DATASET"

        asyncio.run(run_test())

    def test_term_filtering_no_match(self, mock_ckan_settings):
        """Test that datasets not matching all terms are filtered out."""
        import asyncio

        # Setup mock with dataset that doesn't match all terms
        dataset_response = {
            "results": [
                {
                    "id": "dataset-1",
                    "name": "test_dataset",
                    "title": "Test Dataset",
                    "notes": "A test dataset",
                    "organization": {"name": "test_org"},
                    "resources": [],
                    "extras": [],
                }
            ]
        }

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            # Search for terms where one doesn't exist in the dataset
            result = await search_datasets_by_terms(
                ["test", "nonexistent"], server="global"
            )
            assert len(result) == 0  # Should be filtered out

        asyncio.run(run_test())

    def test_extras_json_parsing_success(self, mock_ckan_settings):
        """Test successful JSON parsing of extras."""
        import asyncio

        dataset_response = {
            "results": [
                {
                    "id": "dataset-1",
                    "name": "test_dataset",
                    "title": "Test Dataset",
                    "notes": "A test dataset",
                    "organization": {"name": "test_org"},
                    "resources": [],
                    "extras": [
                        {"key": "mapping", "value": '{"field1": "value1"}'},
                        {"key": "processing", "value": '{"method": "batch"}'},
                    ],
                }
            ]
        }

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            result = await search_datasets_by_terms(["test"], server="global")
            assert len(result) == 1
            assert isinstance(result[0].extras["mapping"], dict)
            assert result[0].extras["mapping"]["field1"] == "value1"
            assert isinstance(result[0].extras["processing"], dict)
            assert result[0].extras["processing"]["method"] == "batch"

        asyncio.run(run_test())

    def test_extras_json_parsing_failure(self, mock_ckan_settings):
        """Test handling of invalid JSON in extras."""
        import asyncio

        dataset_response = {
            "results": [
                {
                    "id": "dataset-1",
                    "name": "test_dataset",
                    "title": "Test Dataset",
                    "notes": "A test dataset",
                    "organization": {"name": "test_org"},
                    "resources": [],
                    "extras": [
                        {"key": "mapping", "value": "invalid json {"},
                        {"key": "processing", "value": "also invalid }"},
                    ],
                }
            ]
        }

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            result = await search_datasets_by_terms(["test"], server="global")
            assert len(result) == 1
            # Should remain as strings when JSON parsing fails
            assert result[0].extras["mapping"] == "invalid json {"
            assert result[0].extras["processing"] == "also invalid }"

        asyncio.run(run_test())

    def test_dataset_without_organization(self, mock_ckan_settings):
        """Test handling dataset without organization."""
        import asyncio

        dataset_response = {
            "results": [
                {
                    "id": "dataset-1",
                    "name": "test_dataset",
                    "title": "Test Dataset",
                    "notes": "A test dataset",
                    "organization": None,
                    "resources": [],
                    "extras": [],
                }
            ]
        }

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = dataset_response
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            result = await search_datasets_by_terms(["test"], server="global")
            assert len(result) == 1
            # Just verify that the dataset was created successfully
            assert result[0].name == "test_dataset"
            assert result[0].title == "Test Dataset"

        asyncio.run(run_test())

    def test_not_found_exception(self, mock_ckan_settings):
        """Test handling of NotFound exception."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.side_effect = NotFound("Not found")
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            result = await search_datasets_by_terms(["test"], server="global")
            assert result == []

        asyncio.run(run_test())

    def test_ckan_api_error_global_server(self, mock_ckan_settings):
        """Test CKANAPIError handling for global server."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.side_effect = CKANAPIError("API Error")
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await search_datasets_by_terms(["test"], server="global")
            assert exc_info.value.status_code == 400
            assert "Global catalog is not reachable" in str(exc_info.value.detail)

        asyncio.run(run_test())

    def test_ckan_api_error_other_server(self, mock_ckan_settings):
        """Test CKANAPIError handling for non-global server."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.side_effect = CKANAPIError("API Error")
        mock_ckan_settings.ckan_no_api_key = mock_ckan

        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await search_datasets_by_terms(["test"], server="local")
            assert exc_info.value.status_code == 400
            assert "Error searching for datasets: API Error" in str(
                exc_info.value.detail
            )

        asyncio.run(run_test())

    def test_general_exception(self, mock_ckan_settings):
        """Test handling of general exceptions."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.side_effect = Exception("General error")
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await search_datasets_by_terms(["test"], server="global")
            assert exc_info.value.status_code == 400
            assert "Error searching for datasets: General error" in str(
                exc_info.value.detail
            )

        asyncio.run(run_test())

    def test_empty_results(self, mock_ckan_settings):
        """Test handling of empty search results."""
        import asyncio

        mock_ckan = MagicMock()
        mock_ckan.action.package_search.return_value = {"results": []}
        mock_ckan_settings.ckan_global = mock_ckan

        async def run_test():
            result = await search_datasets_by_terms(["test"], server="global")
            assert result == []

        asyncio.run(run_test())
