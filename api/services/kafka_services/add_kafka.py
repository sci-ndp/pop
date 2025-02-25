# api/services/kafka_services/add_kafka.py
import json
from typing import Optional
from api.config.ckan_settings import ckan_settings


RESERVED_KEYS = {
    'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection',
    'host', 'port', 'topic', 'mapping', 'processing'
}


def add_kafka(
    dataset_name: str,
    dataset_title: str,
    owner_org: str,
    kafka_topic: str,
    kafka_host: str,
    kafka_port: str,
    dataset_description: Optional[str] = None,
    extras: Optional[dict] = None,
    mapping: Optional[dict] = None,
    processing: Optional[dict] = None,
    ckan_instance=None
) -> str:
    """
    Add a Kafka topic and its metadata to CKAN.

    Parameters
    ----------
    dataset_name : str
        The CKAN dataset name (must be unique).
    dataset_title : str
        The CKAN dataset title.
    owner_org : str
        The CKAN organization ID.
    kafka_topic : str
        The Kafka topic name.
    kafka_host : str
        The Kafka host.
    kafka_port : str
        The Kafka port (integer).
    dataset_description : Optional[str]
        A description for the dataset.
    extras : Optional[dict]
        Additional metadata to store as extras in CKAN.
    mapping : Optional[dict]
        A JSON-serializable dictionary with mapping info.
    processing : Optional[dict]
        A JSON-serializable dictionary with processing info.
    ckan_instance : optional
        A CKAN instance to use for dataset creation. If not provided,
        uses the default `ckan_settings.ckan`.

    Returns
    -------
    str
        The ID of the newly created CKAN dataset.

    Raises
    ------
    ValueError
        If kafka_port is invalid or extras is not a dictionary.
    KeyError
        If extras contains reserved keys.
    Exception
        For errors during dataset or resource creation.
    """

    # Ensure kafka_port is an integer
    if isinstance(kafka_port, str) and kafka_port.isdigit():
        kafka_port = int(kafka_port)
    elif not isinstance(kafka_port, int):
        raise ValueError(
            f"kafka_port must be an integer, got {type(kafka_port)}"
        )

    # Validate extras is a dict or None
    if extras and not isinstance(extras, dict):
        raise ValueError("Extras must be a dictionary or None.")

    # Check reserved keys
    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(
            "Extras contain reserved keys: "
            f"{RESERVED_KEYS.intersection(extras)}"
        )

    # Prepare Kafka-related extras
    kafka_extras = {
        'host': kafka_host,
        'port': kafka_port,
        'topic': kafka_topic
    }

    if mapping:
        kafka_extras['mapping'] = json.dumps(mapping)
    if processing:
        kafka_extras['processing'] = json.dumps(processing)

    # Merge general extras with Kafka extras
    extras_cleaned = extras.copy() if extras else {}
    extras_cleaned.update(kafka_extras)

    # Determine the CKAN instance
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    # Create the CKAN dataset
    try:
        dataset_dict = {
            'name': dataset_name,
            'title': dataset_title,
            'owner_org': owner_org,
            'notes': dataset_description,
            'extras': [
                {'key': k, 'value': v} for k, v in extras_cleaned.items()
            ]
        }
        dataset = ckan_instance.action.package_create(**dataset_dict)
        dataset_id = dataset['id']

    except Exception as exc:
        raise Exception(f"Error creating Kafka dataset: {str(exc)}")

    # Create a Kafka resource within that dataset
    try:
        ckan_instance.action.resource_create(
            package_id=dataset_id,
            name=kafka_topic,
            description=(
                f"Kafka topic {kafka_topic} "
                f"hosted at {kafka_host}:{kafka_port}"
            ),
            format="kafka"
        )
    except Exception as exc:
        raise Exception(f"Error creating Kafka resource: {str(exc)}")

    return dataset_id
