# api/routes/register_routes/post_kafka.py
# Code in English, PEP-8 lines <=79 chars

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, Literal
from api.services import kafka_services
from api.models.request_kafka_model import KafkaDataSourceRequest
from api.services.keycloak_services.get_current_user import get_current_user
from api.config import ckan_settings

router = APIRouter()


@router.post(
    "/kafka",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new Kafka topic",
    description=(
        "Add a Kafka topic and its associated metadata to the system.\n\n"
        "### Required Fields\n"
        "- **dataset_name**: The unique name of the dataset to be created.\n"
        "- **dataset_title**: The title of the dataset to be created.\n"
        "- **owner_org**: The ID of the organization to which the dataset "
        "belongs.\n"
        "- **kafka_topic**: The Kafka topic name.\n"
        "- **kafka_host**: The Kafka host.\n"
        "- **kafka_port**: The Kafka port.\n"
        "- **dataset_description**: A description of the dataset (optional).\n"
        "- **extras**: Additional metadata as CKAN extras (optional).\n"
        "- **mapping**: Mapping information for the dataset (optional).\n"
        "- **processing**: Processing information for the dataset "
        "(optional).\n\n"
        "### Selecting the Server\n"
        "Pass `?server=local` or `?server=pre_ckan` in the query string.\n"
        "If not provided, defaults to 'local'.\n\n"
        "### Example Payload\n"
        "{\n"
        '    \"dataset_name\": \"kafka_topic_example\",\n'
        '    \"dataset_title\": \"Kafka Topic Example\",\n'
        '    \"owner_org\": \"organization_id\",\n'
        '    \"kafka_topic\": \"example_topic\",\n'
        '    \"kafka_host\": \"kafka_host\",\n'
        '    \"kafka_port\": \"kafka_port\",\n'
        '    \"dataset_description\": \"Example Kafka topic.\",\n'
        '    \"extras\": {\n'
        '        \"key1\": \"value1\",\n'
        '        \"key2\": \"value2\"\n'
        '    },\n'
        '    \"mapping\": {\n'
        '        \"field1\": \"mapping1\",\n'
        '        \"field2\": \"mapping2\"\n'
        '    },\n'
        '    \"processing\": {\n'
        '        \"data_key\": \"data\",\n'
        '        \"info_key\": \"info\"\n'
        '    }\n'
        "}\n"
    ),
    responses={
        201: {
            "description": "Kafka dataset created successfully",
            "content": {
                "application/json": {
                    "example": {"id": "12345678-abcd-efgh-ijkl-1234567890ab"}
                }
            }
        },
        409: {
            "description": "Conflict - Duplicate dataset",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Duplicate Dataset",
                            "detail": (
                                "A dataset with the given name or URL "
                                "already exists."
                            )
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error creating Kafka dataset: <error>"
                    }
                }
            }
        }
    }
)
async def create_kafka_datasource(
    data: KafkaDataSourceRequest,
    server: Literal["local", "pre_ckan"] = Query(
        "local",
        description="Specify 'local' or 'pre_ckan'. Defaults to 'local'."
    ),
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add a Kafka topic and its associated metadata to the system.

    If ?server=pre_ckan, uses the pre-CKAN instance. If pre_ckan_enabled is
    False or the URL lacks a valid scheme, returns a 400 error. Otherwise,
    it defaults to local CKAN.

    Parameters
    ----------
    data : KafkaDataSourceRequest
        Required/optional parameters for creating a Kafka dataset/resource.
    server : Literal['local', 'pre_ckan']
        If not provided, defaults to 'local'.
    _ : Dict[str, Any]
        Keycloak user auth (unused).

    Returns
    -------
    dict
        A dictionary containing the ID of the created dataset if successful.

    Raises
    ------
    HTTPException
        - 409: Duplicate dataset
        - 400: Other errors (including "No scheme supplied" for pre_ckan)
    """
    try:
        if server == "pre_ckan":
            if not ckan_settings.pre_ckan_enabled:
                raise HTTPException(
                    status_code=400,
                    detail="Pre-CKAN is disabled and cannot be used."
                )
            ckan_instance = ckan_settings.pre_ckan
        else:
            ckan_instance = ckan_settings.ckan

        dataset_id = kafka_services.add_kafka(
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
            ckan_instance=ckan_instance
        )
        return {"id": dataset_id}

    except Exception as exc:
        error_msg = str(exc)
        if "No scheme supplied" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Server is not configured or unreachable."
            )
        if ("That URL is already in use" in error_msg
                or "That name is already in use" in error_msg):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Duplicate Dataset",
                    "detail": (
                        "A dataset with the given name or URL already exists."
                    )
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
