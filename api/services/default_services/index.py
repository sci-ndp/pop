# api/services/default_services/index.py

from fastapi import Request
from fastapi.templating import Jinja2Templates

from api.config import swagger_settings
from api.config.kafka_settings import kafka_settings
from api.services import status_services
from api.services.keycloak_services.introspect_user_token import \
    get_client_token


def index(request: Request):
    templates = Jinja2Templates(directory="api/templates")

    # Check CKAN status
    try:
        ckan_is_active = status_services.check_ckan_status()

        # Check Keycloak status by attempting to get a client token
        try:
            get_client_token()  # If this succeeds, Keycloak is reachable
            keycloak_is_active = True
        except Exception:
            keycloak_is_active = False

        # Determine the status message based on CKAN and Keycloak statuses
        if ckan_is_active and keycloak_is_active:
            status = "CKAN and Keycloak are active and reachable."
        else:
            if ckan_is_active and not keycloak_is_active:
                status = "CKAN is active, but Keycloak is not reachable."
            elif keycloak_is_active:
                status = "Keycloak is active, but CKAN is not reachable."
            else:
                status = "CKAN and Keycloak are not reachable."
    except Exception:
        status = "CKAN and Keycloak are not reachable."

    # Add Kafka information
    kafka_info = {
        "kafka_host": kafka_settings.kafka_host,
        "kafka_port": kafka_settings.kafka_port,
        "kafka_connection": kafka_settings.kafka_connection,
    }

    # Add JupyterLab settings to context
    use_jupyterlab = swagger_settings.use_jupyterlab
    jupyter_url = swagger_settings.jupyter_url if use_jupyterlab else None

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": swagger_settings.swagger_title,
            "version": swagger_settings.swagger_version,
            "docs_url": f"{request.base_url}docs",
            "status": status,
            "kafka_info": kafka_info,
            "use_jupyterlab": use_jupyterlab,
            "jupyter_url": jupyter_url
        }
    )
