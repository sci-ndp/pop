# tests/test_endpoint_tracking.py

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.services.tracking_services.endpoint_tracker import log_endpoint_access

client = TestClient(app)


class TestEndpointTracker:
    """Test cases for the endpoint tracking functionality."""

    def test_log_endpoint_access_basic(self):
        """Test basic endpoint access logging."""
        with patch("api.services.tracking_services.endpoint_tracker.logger") as mock_logger:
            log_endpoint_access(
                endpoint="/test/endpoint",
                method="GET",
                user_agent="test-agent",
                remote_addr="192.168.1.1",
                status_code=200
            )
            
            # Verify logger was called
            assert mock_logger.info.called
            
            # Get the logged message
            logged_message = mock_logger.info.call_args[0][0]
            assert "ENDPOINT_TRACKING:" in logged_message
            
            # Parse the JSON part
            json_part = logged_message.split("ENDPOINT_TRACKING: ")[1]
            logged_data = json.loads(json_part)
            
            # Verify the logged data
            assert logged_data["endpoint"] == "/test/endpoint"
            assert logged_data["method"] == "GET"
            assert logged_data["user_agent"] == "test-agent"
            assert logged_data["remote_addr"] == "192.168.1.1"
            assert logged_data["status_code"] == 200
            assert "client_id" in logged_data
            assert "organization" in logged_data
            assert "timestamp" in logged_data

    def test_log_endpoint_access_with_request_data(self):
        """Test endpoint access logging with request data."""
        with patch("api.services.tracking_services.endpoint_tracker.logger") as mock_logger:
            request_data = {
                "name": "test_org",
                "title": "Test Organization",
                "description": "Test description"
            }
            query_params = {"server": "local"}
            
            log_endpoint_access(
                endpoint="/organization",
                method="POST",
                user_agent="test-agent",
                remote_addr="192.168.1.1",
                status_code=201,
                request_data=request_data,
                query_params=query_params
            )
            
            # Verify logger was called
            assert mock_logger.info.called
            
            # Get the logged message
            logged_message = mock_logger.info.call_args[0][0]
            json_part = logged_message.split("ENDPOINT_TRACKING: ")[1]
            logged_data = json.loads(json_part)
            
            # Verify the logged data includes request data
            assert logged_data["request_data"]["name"] == "test_org"
            assert logged_data["request_data"]["title"] == "Test Organization"
            assert logged_data["request_data"]["description"] == "Test description"
            assert logged_data["query_params"]["server"] == "local"

    def test_log_endpoint_access_filters_error_responses(self):
        """Test that error responses are not logged."""
        with patch("api.services.tracking_services.endpoint_tracker.logger") as mock_logger:
            # Test with 404 error
            log_endpoint_access(
                endpoint="/test/endpoint",
                method="GET",
                status_code=404
            )
            
            # Test with 500 error
            log_endpoint_access(
                endpoint="/test/endpoint",
                method="GET",
                status_code=500
            )
            
            # Verify logger was not called for error responses
            assert not mock_logger.info.called

    def test_log_endpoint_access_disabled_tracking(self):
        """Test that logging is skipped when tracking is disabled."""
        with patch("api.services.tracking_services.endpoint_tracker.swagger_settings") as mock_settings:
            mock_settings.endpoint_tracking_enabled = False
            
            with patch("api.services.tracking_services.endpoint_tracker.logger") as mock_logger:
                log_endpoint_access(
                    endpoint="/test/endpoint",
                    method="GET",
                    status_code=200
                )
                
                # Verify logger was not called when tracking is disabled
                assert not mock_logger.info.called

    def test_extract_request_data_for_search(self):
        """Test request data extraction for search endpoints."""
        from api.services.tracking_services.endpoint_tracker import _extract_request_data
        
        request_data = {
            "search_term": "climate data",
            "dataset_name": "weather",
            "owner_org": "research",
            "extra_field": "should_be_ignored"
        }
        
        result = _extract_request_data("/search", "GET", request_data)
        
        assert result["search_term"] == "climate data"
        assert result["dataset_name"] == "weather"
        assert result["owner_org"] == "research"
        assert "extra_field" not in result

    def test_extract_request_data_for_organization(self):
        """Test request data extraction for organization endpoints."""
        from api.services.tracking_services.endpoint_tracker import _extract_request_data
        
        request_data = {
            "name": "test_org",
            "title": "Test Organization",
            "description": "Test description",
            "secret_field": "should_be_ignored"
        }
        
        result = _extract_request_data("/organization", "POST", request_data)
        
        assert result["name"] == "test_org"
        assert result["title"] == "Test Organization"
        assert result["description"] == "Test description"
        assert "secret_field" not in result

    def test_log_endpoint_access_error_handling(self):
        """Test error handling in endpoint access logging."""
        with patch("api.services.tracking_services.endpoint_tracker.logger") as mock_logger:
            # Mock datetime to raise an exception
            with patch("api.services.tracking_services.endpoint_tracker.datetime") as mock_datetime:
                mock_datetime.now.side_effect = Exception("Test error")
                
                # This should not raise an exception
                log_endpoint_access("/test", "GET")
                
                # Verify error was logged
                assert mock_logger.error.called
                error_message = mock_logger.error.call_args[0][0]
                assert "Error logging endpoint access" in error_message


class TestEndpointTrackingMiddleware:
    """Test cases for the endpoint tracking middleware."""

    def test_middleware_tracks_endpoint_access(self):
        """Test that middleware tracks endpoint access."""
        with patch("api.services.tracking_services.endpoint_tracker.log_endpoint_access") as mock_log:
            # Make a request to a tracked endpoint
            response = client.get("/status")
            
            # Verify the endpoint was tracked
            assert mock_log.called
            call_args = mock_log.call_args
            assert call_args[1]["endpoint"] == "/status"
            assert call_args[1]["method"] == "GET"
            assert call_args[1]["status_code"] == response.status_code

    def test_middleware_excludes_static_paths(self):
        """Test that middleware excludes static paths."""
        with patch("api.services.tracking_services.endpoint_tracker.log_endpoint_access") as mock_log:
            # Make a request to an excluded path
            response = client.get("/docs")
            
            # Verify the endpoint was NOT tracked
            assert not mock_log.called

    def test_middleware_handles_post_requests(self):
        """Test that middleware handles POST requests."""
        with patch("api.services.tracking_services.endpoint_tracker.log_endpoint_access") as mock_log:
            # Mock authentication
            with patch("api.services.keycloak_services.get_current_user.get_current_user") as mock_auth:
                mock_auth.return_value = {"user": "test_user"}
                
                # Make a POST request
                response = client.post("/token", data={"username": "test", "password": "test"})
                
                # Verify the endpoint was tracked
                assert mock_log.called
                call_args = mock_log.call_args
                assert call_args[1]["endpoint"] == "/token"
                assert call_args[1]["method"] == "POST"

    def test_middleware_handles_errors_gracefully(self):
        """Test that middleware handles errors gracefully."""
        with patch("api.services.tracking_services.endpoint_tracker.log_endpoint_access") as mock_log:
            # Make log_endpoint_access raise an exception
            mock_log.side_effect = Exception("Test error")
            
            # This should not break the request
            response = client.get("/status")
            
            # Response should still be successful
            assert response.status_code == 200

    def test_middleware_gets_client_ip(self):
        """Test that middleware correctly extracts client IP."""
        with patch("api.services.tracking_services.endpoint_tracker.log_endpoint_access") as mock_log:
            # Make a request with X-Forwarded-For header
            headers = {"X-Forwarded-For": "203.0.113.1, 192.168.1.1"}
            response = client.get("/status", headers=headers)
            
            # Verify the correct IP was extracted
            assert mock_log.called
            call_args = mock_log.call_args
            assert call_args[1]["remote_addr"] == "203.0.113.1"
