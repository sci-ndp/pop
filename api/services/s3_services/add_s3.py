from api.config import ckan_settings

RESERVED_KEYS = {
    'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection'
}

def add_s3(
    resource_name,
    resource_title,
    owner_org,
    resource_s3,
    notes="",
    extras=None,
    ckan_instance=None  # Nuevo parámetro opcional
):
    """
    Add an S3 resource to CKAN.

    Parameters
    ----------
    resource_name : str
        The name of the resource to be created.
    resource_title : str
        The title of the resource to be created.
    owner_org : str
        The ID of the organization to which the resource belongs.
    resource_s3 : str
        The S3 URL of the resource to be added.
    notes : str, optional
        Additional notes about the resource (default is an empty string).
    extras : dict, optional
        Additional metadata to be added to the resource package as extras
        (default is None).
    ckan_instance : optional
        A CKAN instance to use for resource creation. If not provided,
        uses the default `ckan_settings.ckan`.

    Returns
    -------
    str
        The ID of the created resource if successful.

    Raises
    ------
    ValueError
        If any input parameter is invalid.
    KeyError
        If any reserved key is found in the extras.
    Exception
        If there is an error creating the resource, an exception is
        raised with a detailed message.
    """
    if not isinstance(extras, (dict, type(None))):
        raise ValueError("Extras must be a dictionary or None.")

    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(
            "Extras contain reserved keys: "
            f"{RESERVED_KEYS.intersection(extras)}"
        )

    # Decide CKAN instance
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    try:
        resource_package_dict = {
            'name': resource_name,
            'title': resource_title,
            'owner_org': owner_org,
            'notes': notes
        }

        if extras:
            resource_package_dict['extras'] = [
                {'key': k, 'value': v} for k, v in extras.items()
            ]

        resource_package = ckan_instance.action.package_create(
            **resource_package_dict
        )
        resource_package_id = resource_package['id']

    except Exception as e:
        raise Exception(f"Error creating resource package: {str(e)}")

    if resource_package_id:
        try:
            ckan_instance.action.resource_create(
                package_id=resource_package_id,
                url=resource_s3,
                name=resource_name,
                description=f"Resource pointing to {resource_s3}",
                format="s3"
            )
        except Exception as e:
            raise Exception(f"Error creating resource: {str(e)}")

        return resource_package_id
    else:
        raise Exception("Unknown error occurred")
