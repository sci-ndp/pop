# api/tasks/metrics_task.py

import logging
import asyncio
from datetime import datetime
from api.services.status_services import get_public_ip, get_system_metrics

logger = logging.getLogger(__name__)


async def record_system_metrics():
    """
    Periodically logs the system metrics:
    Public IP, CPU, memory, and disk usage.
    """
    while True:
        try:
            public_ip = get_public_ip()
            cpu, mem, disk = get_system_metrics()

            logging.info(
                f"Public IP: {public_ip} | "
                f"CPU: {cpu}% | Memory: {mem}% | Disk: {disk}%"
            )
        except Exception as e:
            logging.error(f"Error collecting metrics: {e}")

        await asyncio.sleep(600)  # every 10 minutes (adjustable)
