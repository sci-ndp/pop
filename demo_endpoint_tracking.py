#!/usr/bin/env python3
"""
Demo script to show endpoint tracking functionality.
This script demonstrates how the tracking system works by making sample API calls.
"""

import json
import logging
import time
from datetime import datetime

# Configure logging to show tracking output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Import the tracking function directly
from api.services.tracking_services.endpoint_tracker import log_endpoint_access

def demo_endpoint_tracking():
    """Demonstrate endpoint tracking functionality."""
    
    print("🚀 Endpoint Tracking Demo")
    print("=" * 60)
    
    # Sample endpoint calls that would normally be tracked by middleware
    sample_calls = [
        {
            "endpoint": "/organization",
            "method": "POST",
            "user_agent": "curl/7.68.0",
            "remote_addr": "192.168.1.100",
            "status_code": 201,
            "request_data": {
                "name": "climate_research",
                "title": "Climate Research Organization", 
                "description": "Organization for climate data analysis"
            },
            "query_params": {"server": "local"}
        },
        {
            "endpoint": "/search",
            "method": "GET",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "remote_addr": "203.0.113.45",
            "status_code": 200,
            "request_data": {
                "search_term": "weather data",
                "owner_org": "climate_research"
            },
            "query_params": {"server": "local", "limit": "20"}
        },
        {
            "endpoint": "/kafka",
            "method": "POST",
            "user_agent": "python-requests/2.28.1",
            "remote_addr": "10.0.0.15",
            "status_code": 201,
            "request_data": {
                "dataset_name": "temperature_data",
                "dataset_title": "Temperature Sensor Data",
                "owner_org": "climate_research",
                "kafka_topic": "temperature_sensors"
            }
        },
        {
            "endpoint": "/organization/test-org",
            "method": "DELETE",
            "user_agent": "PostmanRuntime/7.29.2",
            "remote_addr": "172.16.0.5",
            "status_code": 200
        },
        {
            "endpoint": "/status",
            "method": "GET",
            "user_agent": "curl/7.68.0",
            "remote_addr": "192.168.1.100",
            "status_code": 200
        }
    ]
    
    print(f"📋 Simulating {len(sample_calls)} endpoint calls...")
    print()
    
    for i, call in enumerate(sample_calls, 1):
        print(f"📞 Call {i}: {call['method']} {call['endpoint']}")
        
        if 'request_data' in call and call['request_data']:
            print(f"   📄 Request data: {json.dumps(call['request_data'], indent=6)}")
        
        # Log the endpoint access (this is what the middleware does automatically)
        log_endpoint_access(
            endpoint=call["endpoint"],
            method=call["method"],
            user_agent=call["user_agent"],
            remote_addr=call["remote_addr"],
            status_code=call["status_code"],
            request_data=call.get("request_data"),
            query_params=call.get("query_params")
        )
        
        print(f"   ✅ Tracked with status {call['status_code']}")
        print()
        
        # Small delay to show realistic timing
        time.sleep(0.5)
    
    print("🎉 Demo completed!")
    print()
    print("📊 What Gets Tracked:")
    print("• ✅ Only successful requests (HTTP 200-299)")
    print("• ✅ Intelligent data extraction based on endpoint type")
    print("• ✅ User search terms (e.g., 'weather data')")
    print("• ✅ Organization names being created (e.g., 'climate_research')")
    print("• ✅ Dataset/resource names and topics")
    print("• ✅ Client metadata (IP, User-Agent, etc.)")
    print()
    print("📡 Data Destinations:")
    print("• 🌐 External API: Sent to ENDPOINT_TRACKING_API_URL via HTTP POST")
    print("• 📁 Local logs: Saved to logs/metrics.log with 'ENDPOINT_TRACKING:' prefix")
    print("• 🔄 Fallback: If external API fails, local logging continues")
    print()
    print("� Configuration (.env):")
    print("• ENDPOINT_TRACKING_ENABLED=True/False (toggles tracking)")
    print("• ENDPOINT_TRACKING_API_URL=https://your-analytics.api/tracking")
    print("• CLIENT_ID and ORGANIZATION (automatically included)")
    print()
    print("💡 Real-world Usage:")
    print("• When user searches for 'weather data' → tracks search term")
    print("• When user creates org 'climate_research' → tracks org name")
    print("• When user registers Kafka topic → tracks dataset details")
    print("• All tracking happens automatically via middleware")

if __name__ == "__main__":
    demo_endpoint_tracking()
