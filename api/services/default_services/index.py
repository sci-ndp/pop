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

    status = status_services.get_status()

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
