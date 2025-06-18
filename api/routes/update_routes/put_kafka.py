# api/routes/update_routes/put_kafka.py

from typing import Any, Dict, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.config import ckan_settings
from api.models.update_kafka_model import KafkaDataSourceUpdateRequest
from api.services import kafka_services
from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()


@router.put(
    "/kafka/{dataset_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update an existing Kafka topic",
    description=(
        "Update an existing Kafka topic and its associated metadata.\n\n"
        "### Optional Fields\n"
        "- **dataset_name**: The unique name of the dataset.\n"
        "- **dataset_title**: The title of the dataset.\n"
        "- **owner_org**: The ID of the organization.\n"
        "- **kafka_topic**: The Kafka topic name.\n"
        "- **kafka_host**: The Kafka host.\n"
        "- **kafka_port**: The Kafka port.\n"
        "- **dataset_description**: A description of the dataset.\n"
        "- **extras**: Additional metadata to be updated.\n"
        "- **mapping**: Mapping information.\n"
        "- **processing**: Processing information.\n\n"
        "### Query Parameter\n"
        "Use `?server=local` or `?server=pre_ckan` to pick the CKAN instance. "
        "Defaults to 'local' if not provided.\n\n"
        "### Example Payload\n"
        "{\n"
        '    "dataset_name": "kafka_topic_example_updated",\n'
        '    "kafka_topic": "example_topic_updated"\n'
        "}"
    ),
    responses={
        200: {
            "description": "Kafka dataset updated successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Kafka dataset updated successfully"}
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error updating Kafka dataset: <error>"}
                }
            },
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {"example": {"detail": "Kafka dataset not found"}}
            },
        },
    },
)
async def update_kafka_datasource(
    dataset_id: str,
    data: KafkaDataSourceUpdateRequest,
    server: Literal["local", "pre_ckan"] = Query(
        "local", description="Choose 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
    _: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update a Kafka dataset by dataset_id. If ?server=pre_ckan is used,
    the pre_ckan instance is utilized if enabled and valid. Otherwise,
    defaults to local CKAN.

    Raises
    ------
    HTTPException
        - 400: for update errors or invalid server config
        - 404: if dataset not found
    """
    try:
        if server == "pre_ckan":
            if not ckan_settings.pre_ckan_enabled:
                raise HTTPException(
                    status_code=400, detail="Pre-CKAN is disabled and cannot be used."
                )
            ckan_instance = ckan_settings.pre_ckan
        else:
            ckan_instance = ckan_settings.ckan

        updated = kafka_services.update_kafka(
            dataset_id=dataset_id,
            dataset_name=data.dataset_name,
            dataset_title=data.dataset_title,
            owner_org=data.owner_org,
            kafka_topic=data.kafka_topic,
            kafka_host=data.kafka_host,
            kafka_port=data.kafka_port,
            dataset_description=data.dataset_description,
            extras=data.extras,
            mapping=data.mapping,
            processing=data.processing,
            ckan_instance=ckan_instance,  # Pass the chosen instance
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Kafka dataset not found")
        return {"message": "Kafka dataset updated successfully"}

    except HTTPException as he:
        raise he
    except Exception as exc:
        error_msg = str(exc)
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Pre-CKAN server is not configured or unreachable.",
            )
        raise HTTPException(status_code=400, detail=error_msg)
