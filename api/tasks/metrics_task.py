# api/tasks/metrics_task.py

import logging
import asyncio
from api.services.status_services import get_public_ip, get_system_metrics
from api.config.swagger_settings import swagger_settings
from api.config.ckan_settings import ckan_settings
from api.config.kafka_settings import kafka_settings


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

            services = {}

            if swagger_settings.use_jupyterlab:
                services["jupyter"] = swagger_settings.jupyter_url

            if ckan_settings.pre_ckan_enabled:
                services["pre_ckan"] = ckan_settings.pre_ckan_url

            if ckan_settings.ckan_local_enabled:
                services["local_ckan"] = ckan_settings.ckan_url

            if kafka_settings.kafka_connection:
                services["kafka"] = {
                    "host": kafka_settings.kafka_host,
                    "port": kafka_settings.kafka_port,
                    "prefix": kafka_settings.kafka_prefix
                }

            logging.info({
                "public_ip": public_ip,
                "cpu": f"{cpu}%",
                "memory": f"{mem}%",
                "disk": f"{disk}%",
                "services": services
            })

            await asyncio.sleep(600)

        except Exception as e:
            logging.error(f"Error collecting metrics: {e}")
