# api/services/tracking_services/endpoint_tracker.py

import json
import logging
from datetime import datetime
from typing import Optional

import httpx

from api.config.keycloak_settings import keycloak_settings
from api.config.swagger_settings import swagger_settings
from api.config.tracking_settings import tracking_settings

logger = logging.getLogger(__name__)


def log_endpoint_access(
    endpoint: str,
    method: str,
    user_agent: Optional[str] = None,
    remote_addr: Optional[str] = None,
    status_code: Optional[int] = None,
    request_data: Optional[dict] = None,
    query_params: Optional[dict] = None,
) -> None:
    """
    Log endpoint access with tracking information.
    
    Args:
        endpoint: The endpoint path that was accessed
        method: HTTP method used (GET, POST, PUT, DELETE, etc.)
        user_agent: User agent string from the request
        remote_addr: Remote IP address of the client
        status_code: HTTP status code of the response
        request_data: Key request parameters and data (for successful requests only)
        query_params: URL query parameters
    """
    try:
        # Check if tracking is enabled
        if not swagger_settings.endpoint_tracking_enabled:
            return
        
        # Only log successful requests (2xx status codes)
        if status_code is not None and not (200 <= status_code < 300):
            return
        
        # Extract meaningful data from request based on endpoint
        processed_request_data = _extract_request_data(endpoint, method, request_data)
        
        tracking_data = {
            "endpoint": endpoint,
            "method": method.upper(),
            "client_id": keycloak_settings.client_id,
            "organization": swagger_settings.organization,
            "timestamp": datetime.now().isoformat(),
            "user_agent": user_agent,
            "remote_addr": remote_addr,
            "status_code": status_code,
            "request_data": processed_request_data,
            "query_params": query_params,
        }
        
        # Log locally for debugging (optional)
        logger.info(f"ENDPOINT_TRACKING: {json.dumps(tracking_data)}")
        
        # Send to external API endpoint asynchronously
        _send_tracking_data_async(tracking_data)
        
    except Exception as e:
        logger.error(f"Error logging endpoint access: {e}")


def _send_tracking_data_async(tracking_data: dict) -> None:
    """
    Send tracking data to external API endpoint asynchronously.
    
    Args:
        tracking_data: The tracking data to send
    """
    try:
        # Import asyncio here to avoid circular imports
        import asyncio
        
        # Create a background task to send the data
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, schedule the task
            loop.create_task(_send_tracking_data_http(tracking_data))
        else:
            # If no event loop is running, create a new one
            asyncio.run(_send_tracking_data_http(tracking_data))
            
    except Exception as e:
        logger.error(f"Error scheduling tracking data send: {e}")


async def _send_tracking_data_http(tracking_data: dict) -> None:
    """
    Send tracking data to external API endpoint via HTTP POST.
    
    Args:
        tracking_data: The tracking data to send
    """
    try:
        # Check if we have a valid endpoint URL
        if not swagger_settings.endpoint_tracking_api_url or swagger_settings.endpoint_tracking_api_url == "https://api.example.com/endpoint-tracking":
            logger.debug("Endpoint tracking API URL not configured, skipping external send")
            return
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                swagger_settings.endpoint_tracking_api_url,
                json=tracking_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"POP-API/{swagger_settings.swagger_version}",
                    "X-Client-ID": keycloak_settings.client_id,
                    "X-Organization": swagger_settings.organization,
                }
            )
            
            if response.status_code == 200:
                logger.debug(f"Successfully sent tracking data to {swagger_settings.endpoint_tracking_api_url}")
            else:
                logger.warning(f"Failed to send tracking data. Status: {response.status_code}, Response: {response.text}")
                
    except httpx.TimeoutException:
        logger.warning("Timeout sending tracking data to external API")
    except httpx.RequestError as e:
        logger.warning(f"Request error sending tracking data: {e}")
    except Exception as e:
        logger.error(f"Error sending tracking data to external API: {e}")


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
        },
        "/general-dataset": {
            "POST": ["name", "title", "owner_org", "notes"],
            "PUT": ["name", "title", "owner_org", "notes"],
            "PATCH": ["name", "title", "owner_org", "notes"]
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


async def log_endpoint_access_async(
    endpoint: str,
    method: str,
    user_agent: Optional[str] = None,
    remote_addr: Optional[str] = None,
    status_code: Optional[int] = None,
    request_data: Optional[dict] = None,
    query_params: Optional[dict] = None,
) -> None:
    """
    Async version of log_endpoint_access for use in async contexts.
    
    Args:
        endpoint: The endpoint path that was accessed
        method: HTTP method used (GET, POST, PUT, DELETE, etc.)
        user_agent: User agent string from the request
        remote_addr: Remote IP address of the client
        status_code: HTTP status code of the response
        request_data: Key request parameters and data (for successful requests only)
        query_params: URL query parameters
    """
    try:
        # Check if tracking is enabled
        if not swagger_settings.endpoint_tracking_enabled:
            return
        
        # Only log successful requests (2xx status codes)
        if status_code is not None and not (200 <= status_code < 300):
            return
        
        # Extract meaningful data from request based on endpoint
        processed_request_data = _extract_request_data(endpoint, method, request_data)
        
        tracking_data = {
            "endpoint": endpoint,
            "method": method.upper(),
            "client_id": keycloak_settings.client_id,
            "organization": swagger_settings.organization,
            "timestamp": datetime.now().isoformat(),
            "user_agent": user_agent,
            "remote_addr": remote_addr,
            "status_code": status_code,
            "request_data": processed_request_data,
            "query_params": query_params,
        }
        
        # Log locally for debugging (optional)
        logger.info(f"ENDPOINT_TRACKING: {json.dumps(tracking_data)}")
        
        # Send to external API endpoint
        await _send_tracking_data_http(tracking_data)
        
    except Exception as e:
        logger.error(f"Error logging endpoint access: {e}")
