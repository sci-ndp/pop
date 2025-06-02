# api/tasks/metrics_task.py

import logging
import asyncio
import json
import httpx
from api.services.status_services import get_public_ip, get_system_metrics
from api.config.swagger_settings import swagger_settings
from api.config.ckan_settings import ckan_settings
from api.config.kafka_settings import kafka_settings
from api.config.keycloak_settings import keycloak_settings
from api.config.dxspaces_settings import dxspaces_settings

logger = logging.getLogger(__name__)


async def record_system_metrics():
    """
    Periodically logs the system metrics:
    Public IP, CPU, memory, disk usage, API version, and organization.

    Additionally, if public=True, posts the metrics JSON to metrics_endpoint.
    """
    while True:
        metrics_payload = {}

        # First: collect and log metrics
        try:
            public_ip = get_public_ip()
            cpu, mem, disk = get_system_metrics()

            services = {}

            if swagger_settings.use_jupyterlab:
                services["jupyter"] = {
                    "url": swagger_settings.jupyter_url
                }

            if ckan_settings.pre_ckan_enabled:
                services["pre_ckan"] = {
                    "url": ckan_settings.pre_ckan_url,
                    "api_key": ckan_settings.pre_ckan_api_key
                }

            if ckan_settings.ckan_local_enabled:
                services["local_ckan"] = {
                    "url": ckan_settings.ckan_url,
                    "api_key": ckan_settings.ckan_api_key
                }

            services["global_ckan"] = {
                "url": ckan_settings.ckan_global_url
            }

            if kafka_settings.kafka_connection:
                services["kafka"] = {
                    "host": kafka_settings.kafka_host,
                    "port": kafka_settings.kafka_port,
                    "prefix": kafka_settings.kafka_prefix
                }

            if (keycloak_settings.keycloak_enabled
                    and keycloak_settings.keycloak_url):
                services["keycloak"] = {
                    "url": keycloak_settings.keycloak_url,
                    "realm": keycloak_settings.realm_name,
                    "client_id": keycloak_settings.client_id,
                    "client_secret": keycloak_settings.client_secret
                }

            if (dxspaces_settings.dxspaces_enabled
                    and dxspaces_settings.dxspaces_url):
                services["dxspaces"] = {
                    "url": dxspaces_settings.dxspaces_url
                }

            metrics_payload = {
                "public_ip": public_ip,
                "cpu": f"{cpu}%",
                "memory": f"{mem}%",
                "disk": f"{disk}%",
                "version": swagger_settings.swagger_version,
                "organization": swagger_settings.organization,
                "services": services
            }

            # Example logged payload:
            # {
            #     "public_ip": "1.2.3.4",
            #     "cpu": "15%",
            #     "memory": "65%",
            #     "disk": "70%",
            #     "version": "0.6.0",
            #     "organization": "University of Utah",
            #     "services": {...}
            # }
            # Log metrics as JSON
            logger.info(json.dumps(metrics_payload))

        except Exception as e:
            logger.error(
                f"Error collecting metrics: {e},"
                f" error: {metrics_payload}")

        # Second try-except for POST request
        if swagger_settings.public and metrics_payload:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        swagger_settings.metrics_endpoint,
                        json=metrics_payload,
                        timeout=10
                    )
                    response.raise_for_status()
                    logger.info(
                        "Successfully posted metrics to "
                        f"{swagger_settings.metrics_endpoint}"
                    )

            except Exception as e:
                logger.error(f"Error posting metrics: {e}")

        # Sleep before next iteration
        await asyncio.sleep(600)
