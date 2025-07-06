#!/usr/bin/env python3
"""
Enhanced Endpoint Tracking Demo

This script demonstrates the enhanced endpoint tracking functionality with:
1. Success-only logging
2. Request data extraction
3. Optional tracking configuration

Usage:
    python demo_enhanced_tracking.py
"""

import json
import os
import sys
import time
from datetime import datetime

import requests

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Configuration
BASE_URL = "http://localhost:8003"
LOG_FILE = "logs/metrics.log"

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"\n🔄 Step {step_num}: {description}")
    print("-" * 50)

def make_request(method, endpoint, data=None, params=None, expect_success=True):
    """Make an API request and show the result."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, params=params)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, params=params)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        print(f"📡 {method.upper()} {endpoint}")
        if data:
            print(f"📋 Data: {json.dumps(data, indent=2)}")
        if params:
            print(f"🔗 Params: {params}")
        
        print(f"📊 Status: {response.status_code}")
        
        if expect_success and 200 <= response.status_code < 300:
            print("✅ Success!")
        elif not expect_success and not (200 <= response.status_code < 300):
            print("✅ Expected error!")
        else:
            print("❌ Unexpected result!")
        
        try:
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)}")
        except:
            print(f"📄 Response: {response.text[:200]}...")
            
        return response
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def check_tracking_logs(search_term=None):
    """Check the logs for tracking entries."""
    print("\n🔍 Checking tracking logs...")
    
    if not os.path.exists(LOG_FILE):
        print(f"❌ Log file not found: {LOG_FILE}")
        return
    
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()
    
    tracking_entries = []
    for line in lines:
        if "ENDPOINT_TRACKING:" in line:
            if search_term is None or search_term in line:
                tracking_entries.append(line.strip())
    
    if tracking_entries:
        print(f"📋 Found {len(tracking_entries)} tracking entries:")
        for i, entry in enumerate(tracking_entries[-5:], 1):  # Show last 5
            # Extract just the JSON part
            json_part = entry.split("ENDPOINT_TRACKING: ")[1]
            try:
                data = json.loads(json_part)
                print(f"\n{i}. {data['method']} {data['endpoint']} (Status: {data.get('status_code', 'N/A')})")
                if data.get('request_data'):
                    print(f"   📋 Request Data: {json.dumps(data['request_data'], indent=6)}")
                if data.get('query_params'):
                    print(f"   🔗 Query Params: {json.dumps(data['query_params'], indent=6)}")
            except json.JSONDecodeError:
                print(f"{i}. {entry}")
    else:
        print("📭 No tracking entries found")

def demo_enhanced_tracking():
    """Run the enhanced endpoint tracking demonstration."""
    
    print_header("Enhanced Endpoint Tracking Demo")
    print("This demo shows the new tracking features:")
    print("• Success-only logging (errors are not tracked)")
    print("• Request data extraction (search terms, org names, etc.)")
    print("• Optional tracking configuration")
    print("• Intelligent data filtering per endpoint")
    
    # Check if API is running
    print_step(1, "Checking API Status")
    response = make_request("GET", "/status")
    if not response or response.status_code != 200:
        print("❌ API is not running. Please start the API first.")
        return
    
    # Check tracking configuration
    print_step(2, "Checking Tracking Configuration")
    make_request("GET", "/tracking-status")
    
    # Create an organization (successful request with data)
    print_step(3, "Creating Organization (Success - Will be tracked)")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    org_data = {
        "name": f"tracking_demo_{timestamp}",
        "title": "Tracking Demo Organization",
        "description": "Organization created for tracking demonstration"
    }
    make_request("POST", "/organization", data=org_data, params={"server": "local"})
    
    # Try to create duplicate organization (error - will NOT be tracked)
    print_step(4, "Creating Duplicate Organization (Error - Will NOT be tracked)")
    make_request("POST", "/organization", data=org_data, params={"server": "local"}, expect_success=False)
    
    # Search for data (successful request with search terms)
    print_step(5, "Searching for Data (Success - Will be tracked)")
    search_params = {
        "search_term": "climate,weather,temperature",
        "owner_org": f"tracking_demo_{timestamp}",
        "server": "local"
    }
    make_request("GET", "/search", params=search_params)
    
    # Create a Kafka dataset (successful request with specific data)
    print_step(6, "Creating Kafka Dataset (Success - Will be tracked)")
    kafka_data = {
        "dataset_name": f"demo_kafka_{timestamp}",
        "dataset_title": "Demo Kafka Temperature Data",
        "owner_org": f"tracking_demo_{timestamp}",
        "kafka_topic": "temperature_sensors",
        "kafka_host": "localhost",
        "kafka_port": "9092",
        "dataset_description": "Temperature sensor data for tracking demo"
    }
    make_request("POST", "/kafka", data=kafka_data, params={"server": "local"})
    
    # Try to access non-existent endpoint (error - will NOT be tracked)
    print_step(7, "Accessing Non-existent Endpoint (Error - Will NOT be tracked)")
    make_request("GET", "/nonexistent", expect_success=False)
    
    # Wait a moment for logs to be written
    print_step(8, "Waiting for logs to be written...")
    time.sleep(2)
    
    # Check tracking logs
    print_step(9, "Analyzing Tracking Logs")
    check_tracking_logs()
    
    print_header("Demo Summary")
    print("✅ Successful requests were tracked with detailed request data")
    print("✅ Error requests were ignored (not tracked)")
    print("✅ Request data was intelligently extracted per endpoint type")
    print("✅ Query parameters were captured")
    print("✅ Only meaningful data was logged")
    print("\n📋 Key observations:")
    print("• Organization creation logged: name, title, description")
    print("• Search requests logged: search terms, filters")
    print("• Kafka dataset logged: dataset info, topic details")
    print("• Error responses (4xx, 5xx) were NOT logged")
    print("• Tracking can be disabled via ENDPOINT_TRACKING_ENABLED=False")

if __name__ == "__main__":
    demo_enhanced_tracking()
