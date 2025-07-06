# api/middleware/endpoint_tracking_middleware.py

import json
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from api.config.tracking_settings import tracking_settings
from api.services.tracking_services.endpoint_tracker import log_endpoint_access_async

logger = logging.getLogger(__name__)


class EndpointTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track endpoint access across the API.
    
    This middleware follows the existing pattern in the codebase by:
    - Using structured logging (JSON format)
    - Following the services pattern for business logic
    - Using configuration settings from environment variables
    - Maintaining separation of concerns
    """
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        # Exclude paths that shouldn't be tracked (like health checks, static files, etc.)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/openapi.json", 
            "/redoc",
            "/static/",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and track endpoint access.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The HTTP response
        """
        # Check if tracking is enabled
        if not tracking_settings.endpoint_tracking_enabled:
            response = await call_next(request)
            return response
        
        # Get request information early
        method = request.method
        path = request.url.path
        
        # Check if we should exclude this path
        should_exclude = any(path.startswith(exclude_path) for exclude_path in self.exclude_paths)
        
        if should_exclude:
            # Skip tracking for excluded paths
            response = await call_next(request)
            return response
        
        logger.info(f"Processing tracking for: {method} {path}")
        
        # Get additional request information
        user_agent = request.headers.get("user-agent")
        remote_addr = self._get_client_ip(request)
        query_params = dict(request.query_params) if request.query_params else None
        
        # Extract request data for tracking
        request_data = await self._extract_request_data(request)
        
        # Process the request
        response = await call_next(request)
        
        # Log the endpoint access (only for successful requests)
        try:
            await log_endpoint_access_async(
                endpoint=path,
                method=method,
                user_agent=user_agent,
                remote_addr=remote_addr,
                status_code=response.status_code,
                request_data=request_data,
                query_params=query_params
            )
        except Exception as e:
            logger.error(f"Error in endpoint tracking middleware: {e}")
        
        return response
    
    async def _extract_request_data(self, request: Request) -> dict:
        """
        Extract relevant request data for tracking.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            dict: Extracted request data
        """
        request_data = {}
        
        try:
            # Get query parameters
            if request.query_params:
                for key, value in request.query_params.items():
                    request_data[key] = value
            
            # Get JSON body for POST/PUT/PATCH requests
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    body = await request.body()
                    if body:
                        try:
                            json_data = json.loads(body.decode('utf-8'))
                            if isinstance(json_data, dict):
                                request_data.update(json_data)
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            # If we can't parse JSON, skip body data
                            pass
                elif "application/x-www-form-urlencoded" in content_type:
                    # Handle form data (like OAuth token requests)
                    body = await request.body()
                    if body:
                        try:
                            form_data = body.decode('utf-8')
                            # Parse form data
                            for pair in form_data.split('&'):
                                if '=' in pair:
                                    key, value = pair.split('=', 1)
                                    request_data[key] = value
                        except UnicodeDecodeError:
                            pass
            
            return request_data
            
        except Exception as e:
            logger.debug(f"Error extracting request data: {e}")
            return request_data
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get the client's IP address, handling various proxy scenarios.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            str: The client's IP address
        """
        # Check for common proxy headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
