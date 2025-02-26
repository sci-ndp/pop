# api\services\url_services\add_url.py
import json
from api.config import ckan_settings, dxspaces_settings


RESERVED_KEYS = {
    'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection',
    'url', 'mapping', 'processing', 'file_type'
}


def add_url(
    resource_name,
    resource_title,
    owner_org,
    resource_url,
    file_type="",
    notes="",
    extras=None,
    mapping=None,
    processing=None,
    ckan_instance=None  # <-- New param
):
    """
    Add a URL resource to CKAN.

    Parameters
    ----------
    resource_name : str
        The name of the resource to be created.
    resource_title : str
        The title of the resource to be created.
    owner_org : str
        The ID of the organization to which the resource belongs.
    resource_url : str
        The URL of the resource to be added.
    file_type : str, optional
        The type of the file (e.g. 'stream', 'CSV', 'TXT', 'JSON', 'NetCDF').
    notes : str, optional
        Additional notes about the resource (default is an empty string).
    extras : dict, optional
        Additional metadata to be added to the resource package as extras
        (default is None).
    mapping : dict, optional
        Mapping information for the dataset (default is None).
    processing : dict, optional
        Processing information for the dataset based on the file type
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
    ValueError, KeyError, Exception
        If there is any error in validation or creation.
    """

    if not isinstance(extras, (dict, type(None))):
        raise ValueError("Extras must be a dictionary or None.")

    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(
            "Extras contain reserved keys: "
            f"{RESERVED_KEYS.intersection(extras)}"
        )

    # Decide which CKAN instance to use
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    url_extras = {"file_type": file_type}

    if dxspaces_settings.registration_methods['url'] and file_type == "NetCDF":
        dxspaces = dxspaces_settings.dxspaces
        staging_params = {'url': resource_url}
        staging_handle = dxspaces.Register(
            'url', resource_name, staging_params)
        if extras is None:
            extras = {}
        extras['staging_socket'] = dxspaces_settings.dxspaces_url
        extras['staging_handle'] = staging_handle.model_dump_json()

    if mapping:
        url_extras['mapping'] = json.dumps(mapping)
    if processing:
        url_extras['processing'] = json.dumps(processing)

    extras_cleaned = extras.copy() if extras else {}
    extras_cleaned.update(url_extras)

    try:
        resource_package_dict = {
            'name': resource_name,
            'title': resource_title,
            'owner_org': owner_org,
            'notes': notes,
            'extras': [
                {'key': k, 'value': v} for k, v in extras_cleaned.items()
            ]
        }

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
                url=resource_url,
                name=resource_name,
                description=f"Resource pointing to {resource_url}",
                format="url"
            )
        except Exception as e:
            raise Exception(f"Error creating resource: {str(e)}")

        return resource_package_id
    else:
        raise Exception("Unknown error occurred")
