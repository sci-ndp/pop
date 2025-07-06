# api/services/tracking_services/endpoint_tracker.py

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Optional

import httpx

from api.config.keycloak_settings import keycloak_settings
from api.config.swagger_settings import swagger_settings
from api.config.tracking_settings import tracking_settings

logger = logging.getLogger(__name__)


def get_local_timestamp() -> str:
    """
    Get current timestamp in local timezone.
    
    Returns:
        str: Formatted timestamp string
    """
    # Try to get timezone from environment variable first
    timezone_offset = os.getenv('TZ_OFFSET', None)
    
    if timezone_offset:
        # If TZ_OFFSET is set (e.g., "-0600" for MDT), use it
        try:
            offset_hours = int(timezone_offset[:3])
            offset_minutes = int(timezone_offset[3:]) if len(timezone_offset) > 3 else 0
            offset_seconds = offset_hours * 3600 + offset_minutes * 60
            
            # Apply the offset to UTC time
            utc_time = time.time()
            local_time = utc_time + offset_seconds
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(local_time))
        except (ValueError, IndexError):
            pass
    
    # Fallback to system local time
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


async def log_endpoint_access_async(
    endpoint: str,
    method: str,
    user_agent: Optional[str] = None,
    remote_addr: Optional[str] = None,
    status_code: Optional[int] = None,
    request_data: Optional[Dict] = None,
    query_params: Optional[Dict] = None,
) -> None:
    """
    Log endpoint access with tracking information (async version).
    
    Args:
        endpoint: The endpoint path that was accessed
        method: HTTP method used (GET, POST, PUT, DELETE, etc.)
        user_agent: User agent string from the request
        remote_addr: Remote IP address of the client
        status_code: HTTP status code of the response
        request_data: Request data (JSON body, form data, etc.)
        query_params: URL query parameters
    """
    # Check if tracking is enabled
    if not tracking_settings.endpoint_tracking_enabled:
        return
    
    # Only track successful requests (2xx status codes)
    if status_code is not None and not (200 <= status_code < 300):
        return
    
    try:
        # Extract meaningful data from request based on endpoint
        processed_request_data = _extract_request_data(endpoint, method, request_data)
        
        tracking_data = {
            "endpoint": endpoint,
            "method": method.upper(),
            "client_id": keycloak_settings.client_id,
            "organization": swagger_settings.organization,
            "timestamp": get_local_timestamp(),
            "user_agent": user_agent,
            "remote_addr": remote_addr,
            "status_code": status_code,
        }
        
        # Add request data if available
        if processed_request_data:
            tracking_data["request_data"] = processed_request_data
        
        # Add query parameters if available
        if query_params:
            tracking_data["query_params"] = query_params
        
        # Log locally first (for debugging/fallback)
        logger.info(f"ENDPOINT_TRACKING: {json.dumps(tracking_data)}")
        
        # Send to external API
        await send_tracking_data_to_external_api(tracking_data)
        
    except Exception as e:
        logger.error(f"Error logging endpoint access: {e}")


async def send_tracking_data_to_external_api(tracking_data: dict) -> None:
    """
    Send tracking data to external API endpoint.
    
    Args:
        tracking_data: Dictionary containing tracking information
    """
    try:
        # Check if external API URL is configured and not the placeholder
        if (not tracking_settings.endpoint_tracking_api_url or 
            tracking_settings.endpoint_tracking_api_url == "https://api.example.com/endpoint-tracking"):
            logger.debug("External tracking API URL not configured, skipping external send")
            return
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Client-ID": keycloak_settings.client_id,
            "X-Organization": swagger_settings.organization,
            "User-Agent": f"POP-API/{swagger_settings.swagger_version}",
        }
        
        # Send HTTP POST request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                tracking_settings.endpoint_tracking_api_url,
                json=tracking_data,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            logger.debug(f"Successfully sent tracking data to {tracking_settings.endpoint_tracking_api_url}")
            
    except httpx.TimeoutException:
        logger.warning(f"Timeout sending tracking data to {tracking_settings.endpoint_tracking_api_url}")
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error sending tracking data: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.warning(f"Error sending tracking data to external API: {e}")


def _extract_request_data(endpoint: str, method: str, request_data: Optional[dict]) -> Optional[dict]:
    """
    Extract meaningful data from requests based on endpoint and method.
    
    Args:
        endpoint: The endpoint path
        method: HTTP method
        request_data: Raw request data
        
    Returns:
        dict: Processed request data with relevant fields
    """
    if not request_data:
        return None
    
    # Define what data to extract for each endpoint
    extraction_rules = {
        "/organization": {
            "POST": ["name", "title", "description"],
            "GET": ["name"]
        },
        "/search": {
            "GET": ["search_term", "dataset_name", "dataset_title", "owner_org", "resource_format"],
            "POST": ["search_term", "dataset_name", "dataset_title", "owner_org", "resource_format"]
        },
        "/kafka": {
            "POST": ["dataset_name", "dataset_title", "owner_org", "kafka_topic"],
            "PUT": ["dataset_name", "dataset_title", "owner_org", "kafka_topic"]
        },
        "/s3": {
            "POST": ["resource_name", "resource_title", "owner_org", "s3_bucket"],
            "PUT": ["resource_name", "resource_title", "owner_org", "s3_bucket"]
        },
        "/url": {
            "POST": ["resource_name", "resource_title", "owner_org", "resource_url"],
            "PUT": ["resource_name", "resource_title", "owner_org", "resource_url"]
        },
        "/services": {
            "POST": ["service_name", "service_title", "owner_org", "service_url"],
            "PUT": ["service_name", "service_title", "owner_org", "service_url"]
        }
    }
    
    # Find matching rule
    for endpoint_pattern, methods in extraction_rules.items():
        if endpoint_pattern in endpoint:
            if method.upper() in methods:
                fields_to_extract = methods[method.upper()]
                extracted_data = {}
                
                for field in fields_to_extract:
                    if field in request_data:
                        extracted_data[field] = request_data[field]
                
                return extracted_data if extracted_data else None
    
    return None


def log_endpoint_access(
    endpoint: str,
    method: str,
    user_agent: Optional[str] = None,
    remote_addr: Optional[str] = None,
    status_code: Optional[int] = None,
    request_data: Optional[Dict] = None,
    query_params: Optional[Dict] = None,
) -> None:
    """
    Log endpoint access with tracking information (sync version).
    
    Args:
        endpoint: The endpoint path that was accessed
        method: HTTP method used (GET, POST, PUT, DELETE, etc.)
        user_agent: User agent string from the request
        remote_addr: Remote IP address of the client
        status_code: HTTP status code of the response
        request_data: Request data (JSON body, form data, etc.)
        query_params: URL query parameters
    """
    # Check if tracking is enabled
    if not tracking_settings.endpoint_tracking_enabled:
        return
    
    # Only track successful requests (2xx status codes)
    if status_code is not None and not (200 <= status_code < 300):
        return
    
    try:
        # Extract meaningful data from request based on endpoint
        processed_request_data = _extract_request_data(endpoint, method, request_data)
        
        tracking_data = {
            "endpoint": endpoint,
            "method": method.upper(),
            "client_id": keycloak_settings.client_id,
            "organization": swagger_settings.organization,
            "timestamp": get_local_timestamp(),
            "user_agent": user_agent,
            "remote_addr": remote_addr,
            "status_code": status_code,
        }
        
        # Add request data if available
        if processed_request_data:
            tracking_data["request_data"] = processed_request_data
        
        # Add query parameters if available
        if query_params:
            tracking_data["query_params"] = query_params
        
        # Log locally (for debugging/fallback)
        logger.info(f"ENDPOINT_TRACKING: {json.dumps(tracking_data)}")
        
        # Note: Sync version only does local logging
        # For external API, use the async version
        
    except Exception as e:
        logger.error(f"Error logging endpoint access: {e}")
