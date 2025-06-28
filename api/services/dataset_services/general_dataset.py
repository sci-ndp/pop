# api/services/dataset_services/general_dataset.py

from typing import Any, Dict, List, Optional

from api.config.ckan_settings import ckan_settings

RESERVED_KEYS = {
    "name",
    "title",
    "owner_org",
    "notes",
    "id",
    "resources",
    "tags",
    "private",
    "license_id",
    "version",
    "state",
}


def create_general_dataset(
    name: str,
    title: str,
    owner_org: str,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
    extras: Optional[Dict[str, Any]] = None,
    resources: Optional[List[Dict[str, Any]]] = None,
    private: Optional[bool] = False,
    license_id: Optional[str] = None,
    version: Optional[str] = None,
    ckan_instance=None,
) -> str:
    """
    Create a general dataset in CKAN.

    Parameters
    ----------
    name : str
        The unique name for the dataset.
    title : str
        The human-readable title of the dataset.
    owner_org : str
        The organization ID that owns this dataset.
    notes : Optional[str]
        Description or notes about the dataset.
    tags : Optional[List[str]]
        List of tags for categorizing the dataset.
    extras : Optional[Dict[str, Any]]
        Additional metadata as key-value pairs.
    resources : Optional[List[Dict[str, Any]]]
        List of resources associated with this dataset.
    private : Optional[bool]
        Whether the dataset is private or public.
    license_id : Optional[str]
        License identifier for the dataset.
    version : Optional[str]
        Version of the dataset.
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
        If extras is not a dictionary or contains invalid data.
    KeyError
        If extras contains reserved keys.
    Exception
        For errors during dataset creation.
    """
    # Validate extras is a dict or None
    if extras and not isinstance(extras, dict):
        raise ValueError("Extras must be a dictionary or None.")

    # Check reserved keys
    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(
            "Extras contain reserved keys: " f"{RESERVED_KEYS.intersection(extras)}"
        )

    # Determine the CKAN instance
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    # Prepare dataset dictionary
    dataset_dict = {
        "name": name,
        "title": title,
        "owner_org": owner_org,
        "private": private,
    }

    # Add optional fields if provided
    if notes:
        dataset_dict["notes"] = notes
    if license_id:
        dataset_dict["license_id"] = license_id
    if version:
        dataset_dict["version"] = version

    # Handle tags
    if tags:
        dataset_dict["tags"] = [{"name": tag} for tag in tags]

    # Handle extras
    if extras:
        dataset_dict["extras"] = [{"key": k, "value": v} for k, v in extras.items()]

    # Create the CKAN dataset
    try:
        dataset = ckan_instance.action.package_create(**dataset_dict)
        dataset_id = dataset["id"]
    except Exception as exc:
        raise Exception(f"Error creating general dataset: {str(exc)}")

    # Create resources if provided
    if resources:
        try:
            for resource in resources:
                resource_dict = resource.copy()
                resource_dict["package_id"] = dataset_id
                ckan_instance.action.resource_create(**resource_dict)
        except Exception as exc:
            raise Exception(f"Error creating dataset resources: {str(exc)}")

    return dataset_id


def update_general_dataset(
    dataset_id: str,
    name: Optional[str] = None,
    title: Optional[str] = None,
    owner_org: Optional[str] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
    extras: Optional[Dict[str, Any]] = None,
    resources: Optional[List[Dict[str, Any]]] = None,
    private: Optional[bool] = None,
    license_id: Optional[str] = None,
    version: Optional[str] = None,
    ckan_instance=None,
) -> str:
    """
    Update a general dataset in CKAN (full replacement).

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to update.
    name : Optional[str]
        The unique name for the dataset.
    title : Optional[str]
        The human-readable title of the dataset.
    owner_org : Optional[str]
        The organization ID that owns this dataset.
    notes : Optional[str]
        Description or notes about the dataset.
    tags : Optional[List[str]]
        List of tags for categorizing the dataset.
    extras : Optional[Dict[str, Any]]
        Additional metadata as key-value pairs.
    resources : Optional[List[Dict[str, Any]]]
        List of resources associated with this dataset.
    private : Optional[bool]
        Whether the dataset is private or public.
    license_id : Optional[str]
        License identifier for the dataset.
    version : Optional[str]
        Version of the dataset.
    ckan_instance : optional
        A CKAN instance to use for dataset update. If not provided,
        uses the default `ckan_settings.ckan`.

    Returns
    -------
    str
        The ID of the updated CKAN dataset.

    Raises
    ------
    ValueError
        If extras is not a dictionary.
    KeyError
        If extras contains reserved keys.
    Exception
        For errors during dataset update.
    """
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    # Validate extras
    if extras and not isinstance(extras, dict):
        raise ValueError("Extras must be a dictionary or None.")

    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(
            "Extras contain reserved keys: " f"{RESERVED_KEYS.intersection(extras)}"
        )

    try:
        # Fetch the existing dataset
        dataset = ckan_instance.action.package_show(id=dataset_id)
    except Exception as exc:
        raise Exception(f"Error fetching dataset: {str(exc)}")

    # Update fields with new values or keep existing ones
    dataset["name"] = name or dataset.get("name")
    dataset["title"] = title or dataset.get("title")
    dataset["owner_org"] = owner_org or dataset.get("owner_org")

    if notes is not None:
        dataset["notes"] = notes
    if private is not None:
        dataset["private"] = private
    if license_id is not None:
        dataset["license_id"] = license_id
    if version is not None:
        dataset["version"] = version

    # Handle tags
    if tags is not None:
        dataset["tags"] = [{"name": tag} for tag in tags]

    # Handle extras - merge with existing if provided
    if extras is not None:
        current_extras = {
            extra["key"]: extra["value"] for extra in dataset.get("extras", [])
        }
        current_extras.update(extras)
        dataset["extras"] = [{"key": k, "value": v} for k, v in current_extras.items()]

    try:
        updated_dataset = ckan_instance.action.package_update(**dataset)
        return updated_dataset["id"]
    except Exception as exc:
        raise Exception(f"Error updating general dataset: {str(exc)}")


def patch_general_dataset(
    dataset_id: str,
    name: Optional[str] = None,
    title: Optional[str] = None,
    owner_org: Optional[str] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
    extras: Optional[Dict[str, Any]] = None,
    resources: Optional[List[Dict[str, Any]]] = None,
    private: Optional[bool] = None,
    license_id: Optional[str] = None,
    version: Optional[str] = None,
    ckan_instance=None,
) -> str:
    """
    Partially update a general dataset in CKAN.

    Only updates the fields that are provided, leaving others unchanged.

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to patch.
    name : Optional[str]
        The unique name for the dataset.
    title : Optional[str]
        The human-readable title of the dataset.
    owner_org : Optional[str]
        The organization ID that owns this dataset.
    notes : Optional[str]
        Description or notes about the dataset.
    tags : Optional[List[str]]
        List of tags for categorizing the dataset.
    extras : Optional[Dict[str, Any]]
        Additional metadata as key-value pairs to merge.
    resources : Optional[List[Dict[str, Any]]]
        List of resources associated with this dataset.
    private : Optional[bool]
        Whether the dataset is private or public.
    license_id : Optional[str]
        License identifier for the dataset.
    version : Optional[str]
        Version of the dataset.
    ckan_instance : optional
        A CKAN instance to use for dataset patch. If not provided,
        uses the default `ckan_settings.ckan`.

    Returns
    -------
    str
        The ID of the patched CKAN dataset.

    Raises
    ------
    ValueError
        If extras is not a dictionary.
    KeyError
        If extras contains reserved keys.
    Exception
        For errors during dataset patch.
    """
    # For PATCH, we use the same logic as PUT but only update provided fields
    return update_general_dataset(
        dataset_id=dataset_id,
        name=name,
        title=title,
        owner_org=owner_org,
        notes=notes,
        tags=tags,
        extras=extras,
        resources=resources,
        private=private,
        license_id=license_id,
        version=version,
        ckan_instance=ckan_instance,
    )
