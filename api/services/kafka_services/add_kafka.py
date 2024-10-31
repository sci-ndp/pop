import json
from api.config.ckan_settings import ckan_settings


# Define a set of reserved keys that should not be used in the extras
RESERVED_KEYS = {
    'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection',
    'host', 'port', 'topic', 'mapping', 'processing'}


def add_kafka(dataset_name,
              dataset_title,
              owner_org,
              kafka_topic,
              kafka_host,
              kafka_port,
              dataset_description,
              extras=None,
              mapping=None,
              processing=None):
    """
    Add a Kafka topic and its associated metadata to the system.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to be created.
    dataset_title : str
        The title of the dataset to be created.
    owner_org : str
        The ID of the organization to which the dataset belongs.
    kafka_topic : str
        The Kafka topic name.
    kafka_host : str
        The Kafka host.
    kafka_port : str
        The Kafka port.
    dataset_description : str, optional
        A description of the dataset (default is an empty string).
    extras : dict, optional
        Additional metadata to be added to the dataset as extras
        (default is None).
    mapping : dict, optional
        Mapping information for the dataset (default is None).
    processing : dict, optional
        Processing information for the dataset (default is None).

    Returns
    -------
    str
        The ID of the created dataset if successful.

    Raises
    ------
    ValueError
        If any input parameter is invalid.
    KeyError
        If any reserved key is found in the extras.
    Exception
        If there is an error creating the dataset or adding the resource, an
        exception is raised with a detailed message.
    """

    if isinstance(kafka_port, str) and kafka_port.isdigit():
        kafka_port = int(kafka_port)
    elif not isinstance(kafka_port, int):
        raise ValueError(
            f"kafka_port must be an integer, got {type(kafka_port)}")

    if not isinstance(extras, (dict, type(None))):
        raise ValueError("Extras must be a dictionary or None.")

    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(
            "Extras contain reserved keys: "
            f"{RESERVED_KEYS.intersection(extras)}")

    kafka_extras = {
        'host': kafka_host,
        'port': kafka_port,
        'topic': kafka_topic
    }

    if mapping:
        kafka_extras['mapping'] = json.dumps(mapping)

    if processing:
        kafka_extras['processing'] = json.dumps(processing)

    extras_cleaned = extras.copy() if extras else {}
    extras_cleaned.update(kafka_extras)

    ckan = ckan_settings.ckan

    try:
        # Create the dataset in CKAN with additional extras if provided
        dataset_dict = {
            'name': dataset_name,
            'title': dataset_title,
            'owner_org': owner_org,
            'notes': dataset_description,
            'extras': [
                {'key': k, 'value': v} for k, v in extras_cleaned.items()]
        }

        dataset = ckan.action.package_create(**dataset_dict)

        # Retrieve the dataset ID
        dataset_id = dataset['id']
    except Exception as e:
        # If an error occurs, raise an exception with a detailed error message
        raise Exception(f"Error creating Kafka dataset: {str(e)}")

    if dataset_id:
        try:
            # Create the resource within the newly created dataset
            ckan.action.resource_create(
                package_id=dataset_id,
                name=kafka_topic,
                description=(
                    f"Kafka topic {kafka_topic} "
                    f"hosted at {kafka_host}:{kafka_port}"),
                format="kafka"
            )
        except Exception as e:
            # If an error occurs, raise an exception with a detailed error
            # message
            raise Exception(f"Error creating Kafka resource: {str(e)}")

        # If everything goes well, return the dataset ID
        return dataset_id
    else:
        # This shouldn't happen as the dataset creation should either succeed
        # or raise an exception
        raise Exception("Unknown error occurred")
