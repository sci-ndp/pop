#!/usr/bin/env python3
"""
Enhanced demo script to show endpoint tracking functionality with external API calls.
This script demonstrates how the tracking system works by making sample API calls
and showing how data is sent to external endpoints.
"""

import json
import logging
import time
from datetime import datetime
import asyncio

# Configure logging to show tracking output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

print("🚀 Enhanced Endpoint Tracking Demo")
print("=" * 60)
print()
print("This demo shows the new features:")
print("✅ Success-only logging (2xx status codes)")
print("✅ Request data extraction")
print("✅ External API integration")
print("✅ Optional tracking via ENDPOINT_TRACKING_ENABLED")
print()

print("🔧 Configuration Settings:")
print("• ENDPOINT_TRACKING_ENABLED=True/False (enable/disable tracking)")
print("• ENDPOINT_TRACKING_API_URL=<your-endpoint> (where to send data)")
print("• CLIENT_ID=<your-client-id> (from Keycloak)")
print("• ORGANIZATION=<your-org> (your organization name)")
print()

print("📊 What Gets Tracked:")
print("• Endpoint path and HTTP method")
print("• Client ID and Organization from .env")
print("• Request data (search terms, org names, etc.)")
print("• User agent and client IP")
print("• Timestamp and status code")
print("• Query parameters")
print()

print("📡 External API Integration:")
print("• Tracking data is sent via HTTP POST to ENDPOINT_TRACKING_API_URL")
print("• JSON payload with all tracking information")
print("• Asynchronous sending - doesn't block API responses")
print("• Graceful error handling if external API is unavailable")
print("• Local logging is also maintained for debugging")
print()

print("📋 Sample Tracking Payload:")
sample_payload = {
    "endpoint": "/organization",
    "method": "POST",
    "client_id": "saleem_test",
    "organization": "SCI - University of Utah",
    "timestamp": datetime.now().isoformat(),
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "remote_addr": "192.168.1.100",
    "status_code": 201,
    "request_data": {
        "name": "climate_research",
        "title": "Climate Research Organization",
        "description": "Organization for climate data analysis"
    },
    "query_params": {
        "server": "local"
    }
}
print(json.dumps(sample_payload, indent=2))
print()

print("🎯 Key Features:")
print("✅ Only successful requests (200-299) are tracked")
print("✅ Error requests are ignored for clean analytics")
print("✅ Intelligent request data extraction based on endpoint")
print("✅ Optional tracking - can be disabled via environment variable")
print("✅ External API integration with fallback to local logging")
print("✅ Non-blocking asynchronous operation")
print("✅ Comprehensive error handling")
print()

print("🔍 Real-World Examples:")
print()

examples = [
    {
        "action": "User creates organization 'weather_research'",
        "endpoint": "/organization",
        "method": "POST",
        "tracked_data": {
            "name": "weather_research",
            "title": "Weather Research Lab",
            "description": "Organization for weather data analysis"
        }
    },
    {
        "action": "User searches for 'temperature sensors'",
        "endpoint": "/search",
        "method": "GET",
        "tracked_data": {
            "search_term": "temperature sensors",
            "owner_org": "weather_research",
            "resource_format": "csv"
        }
    },
    {
        "action": "User registers Kafka topic 'sensor_data'",
        "endpoint": "/kafka",
        "method": "POST",
        "tracked_data": {
            "dataset_name": "sensor_readings",
            "dataset_title": "Real-time Sensor Data",
            "kafka_topic": "sensor_data"
        }
    }
]

for i, example in enumerate(examples, 1):
    print(f"{i}. {example['action']}")
    print(f"   → {example['method']} {example['endpoint']}")
    print(f"   → Tracked: {json.dumps(example['tracked_data'])}")
    print()

print("🚀 Integration Steps:")
print("1. Set ENDPOINT_TRACKING_ENABLED=True in .env")
print("2. Set ENDPOINT_TRACKING_API_URL to your tracking endpoint")
print("3. Ensure CLIENT_ID and ORGANIZATION are configured")
print("4. Start your API - tracking happens automatically!")
print("5. Check your external API for incoming tracking data")
print()

print("🎉 The tracking system is now ready to capture meaningful API usage data!")
print("All successful operations will be tracked and sent to your external analytics endpoint.")

if __name__ == "__main__":
    pass
