# api/utils/system_metrics.py

import psutil
import requests


def get_public_ip():
    """Retrieve the public IP address using external API."""
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        return response.json().get("ip")
    except requests.RequestException as e:
        return f"Error retrieving IP: {e}"


def get_system_metrics():
    """Get system metrics: CPU, memory, and disk usage percentages."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_usage_percent = psutil.disk_usage("/").percent
    return cpu_percent, memory_percent, disk_usage_percent
