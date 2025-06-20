# tests/test_urlrequest_model.py
import pytest

from api.models.urlrequest_model import (
    CSVProcessingInfo,
    FileTypeEnum,
    JSONProcessingInfo,
    NetCDFProcessingInfo,
    StreamProcessingInfo,
    TXTProcessingInfo,
    URLRequest,
)


class TestFileTypeEnum:
    """Test cases for FileTypeEnum."""

    def test_file_type_enum_values(self):
        """Test FileTypeEnum contains expected values."""
        assert FileTypeEnum.stream == "stream"
        assert FileTypeEnum.CSV == "CSV"
        assert FileTypeEnum.TXT == "TXT"
        assert FileTypeEnum.JSON == "JSON"
        assert FileTypeEnum.NetCDF == "NetCDF"


class TestProcessingInfoModels:
    """Test cases for processing info models."""

    def test_stream_processing_info(self):
        """Test StreamProcessingInfo model."""
        info = StreamProcessingInfo(refresh_rate="5 seconds", data_key="results")
        assert info.refresh_rate == "5 seconds"
        assert info.data_key == "results"

    def test_csv_processing_info(self):
        """Test CSVProcessingInfo model."""
        info = CSVProcessingInfo(
            delimiter=",", header_line=1, start_line=2, comment_char="#"
        )
        assert info.delimiter == ","
        assert info.header_line == 1
        assert info.start_line == 2
        assert info.comment_char == "#"

    def test_txt_processing_info(self):
        """Test TXTProcessingInfo model."""
        info = TXTProcessingInfo(delimiter="\t", header_line=1, start_line=2)
        assert info.delimiter == "\t"
        assert info.header_line == 1
        assert info.start_line == 2

    def test_json_processing_info(self):
        """Test JSONProcessingInfo model."""
        info = JSONProcessingInfo(
            info_key="count", additional_key="metadata", data_key="results"
        )
        assert info.info_key == "count"
        assert info.additional_key == "metadata"
        assert info.data_key == "results"

    def test_netcdf_processing_info(self):
        """Test NetCDFProcessingInfo model."""
        info = NetCDFProcessingInfo(group="group_name")
        assert info.group == "group_name"


class TestURLRequest:
    """Test cases for URLRequest model."""

    def test_url_request_minimal(self):
        """Test URLRequest with minimal required fields."""
        request = URLRequest(
            resource_name="test_resource",
            resource_title="Test Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.csv",
        )

        assert request.resource_name == "test_resource"
        assert request.resource_title == "Test Resource"
        assert request.owner_org == "test_org"
        assert request.resource_url == "http://example.com/data.csv"
        assert request.file_type is None
        assert request.notes is None
        assert request.extras is None
        assert request.mapping is None
        assert request.processing is None

    def test_url_request_with_valid_processing(self):
        """Test URLRequest with valid processing for known file types."""
        # Test CSV processing
        csv_request = URLRequest(
            resource_name="csv_resource",
            resource_title="CSV Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.csv",
            file_type="CSV",
            processing={
                "delimiter": ",",
                "header_line": 1,
                "start_line": 2,
                "comment_char": "#",
            },
        )
        assert csv_request.file_type == "CSV"

        # Test JSON processing
        json_request = URLRequest(
            resource_name="json_resource",
            resource_title="JSON Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.json",
            file_type="JSON",
            processing={"info_key": "count", "data_key": "results"},
        )
        assert json_request.file_type == "JSON"

    def test_url_request_with_edge_case_processing(self):
        """Test URLRequest processing validation edge cases."""
        # Test that the validation actually works for proper cases
        request = URLRequest(
            resource_name="edge_case_resource",
            resource_title="Edge Case Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.csv",
            file_type="CSV",
            processing={"delimiter": ",", "header_line": 1},  # Valid processing
        )
        assert request.file_type == "CSV"

    def test_url_request_validation_error_handling(self):
        """Test that ValidationError is properly handled and re-raised as ValueError."""
        # Force a ValidationError by providing invalid data type
        with pytest.raises(ValueError, match="Invalid processing info"):
            URLRequest(
                resource_name="validation_test",
                resource_title="Validation Test",
                owner_org="test_org",
                resource_url="http://example.com/data.csv",
                file_type="CSV",
                processing={
                    "header_line": "not_an_integer",  # This should cause ValidationError
                    "delimiter": ",",
                },
            )

    def test_url_request_with_custom_file_type(self):
        """Test URLRequest with custom file type (no validation)."""
        request = URLRequest(
            resource_name="custom_resource",
            resource_title="Custom Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.custom",
            file_type="CUSTOM_TYPE",
            processing={"any_field": "any_value"},  # Should be allowed for custom types
        )
        assert request.file_type == "CUSTOM_TYPE"
        assert request.processing == {"any_field": "any_value"}

    def test_url_request_no_processing(self):
        """Test URLRequest with no processing (should pass validation)."""
        request = URLRequest(
            resource_name="no_processing",
            resource_title="No Processing Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.csv",
            file_type="CSV",
            # No processing field
        )
        assert request.processing is None

    def test_url_request_all_fields(self):
        """Test URLRequest with all fields provided."""
        request = URLRequest(
            resource_name="full_resource",
            resource_title="Full Resource",
            owner_org="test_org",
            resource_url="http://example.com/data.json",
            file_type="JSON",
            notes="Test notes",
            extras={"key1": "value1", "key2": "value2"},
            mapping={"field1": "mapping1", "field2": "mapping2"},
            processing={"data_key": "data", "info_key": "info"},
        )

        assert request.notes == "Test notes"
        assert request.extras == {"key1": "value1", "key2": "value2"}
        assert request.mapping == {"field1": "mapping1", "field2": "mapping2"}
        assert request.processing == {"data_key": "data", "info_key": "info"}
