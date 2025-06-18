# api/services/service_services/add_service.py
from typing import Any, Dict, Optional

from api.config import ckan_settings

RESERVED_KEYS = {
    "name",
    "title",
    "owner_org",
    "notes",
    "id",
    "resources",
    "collection",
    "service_url",
    "service_type",
    "health_check_url",
    "documentation_url",
}


def add_service(
    service_name: str,
    service_title: str,
    owner_org: str,
    service_url: str,
    service_type: Optional[str] = None,
    notes: Optional[str] = None,
    extras: Optional[Dict[str, Any]] = None,
    health_check_url: Optional[str] = None,
    documentation_url: Optional[str] = None,
    ckan_instance=None,
) -> str:
    """
    Add a service resource to CKAN.

    This function creates a new service dataset in CKAN with the provided
    metadata and creates an associated resource pointing to the service URL.

    Parameters
    ----------
    service_name : str
        The unique name of the service to be created.
    service_title : str
        The display title of the service to be created.
    owner_org : str
        The ID of the organization (must be 'services').
    service_url : str
        The URL where the service is accessible.
    service_type : Optional[str]
        The type of service (e.g., 'API', 'Web Service', 'Microservice').
    notes : Optional[str]
        Additional notes about the service (default is None).
    extras : Optional[Dict[str, Any]]
        Additional metadata to be added to the service package as extras
        (default is None).
    health_check_url : Optional[str]
        URL for service health check endpoint (default is None).
    documentation_url : Optional[str]
        URL to service documentation (default is None).
    ckan_instance : optional
        A CKAN instance to use for service creation. If not provided,
        uses the default `ckan_settings.ckan`.

    Returns
    -------
    str
        The ID of the created service dataset if successful.

    Raises
    ------
    ValueError
        If any input parameter is invalid or owner_org is not 'services'.
    KeyError
        If any reserved key is found in the extras.
    Exception
        If there is an error creating the service, an exception is
        raised with a detailed message.
    """
    # Validate owner_org must be 'services'
    if owner_org != "services":
        raise ValueError("owner_org must be 'services' for service registration")

    # Validate extras parameter
    if not isinstance(extras, (dict, type(None))):
        raise ValueError("Extras must be a dictionary or None.")

    # Check for reserved keys in extras
    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(
            "Extras contain reserved keys: " f"{RESERVED_KEYS.intersection(extras)}"
        )

    # Decide CKAN instance
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    # Prepare service-specific extras
    service_extras = {}
    if service_type:
        service_extras["service_type"] = service_type
    if health_check_url:
        service_extras["health_check_url"] = health_check_url
    if documentation_url:
        service_extras["documentation_url"] = documentation_url

    # Merge user extras with service-specific extras
    extras_cleaned = extras.copy() if extras else {}
    extras_cleaned.update(service_extras)

    try:
        # Create the service package/dataset in CKAN
        service_package_dict = {
            "name": service_name,
            "title": service_title,
            "owner_org": owner_org,
            "notes": notes or f"Service: {service_title}",
        }

        # Add extras if any
        if extras_cleaned:
            service_package_dict["extras"] = [
                {"key": k, "value": v} for k, v in extras_cleaned.items()
            ]

        service_package = ckan_instance.action.package_create(**service_package_dict)
        service_package_id = service_package["id"]

    except Exception as exc:
        raise Exception(f"Error creating service package: {str(exc)}")

    # Create the service resource within the dataset
    if service_package_id:
        try:
            resource_description = (
                f"Service endpoint for {service_title} " f"accessible at {service_url}"
            )

            ckan_instance.action.resource_create(
                package_id=service_package_id,
                url=service_url,
                name=service_name,
                description=resource_description,
                format="service",
            )
        except Exception as exc:
            raise Exception(f"Error creating service resource: {str(exc)}")

        return service_package_id
    else:
        raise Exception("Unknown error occurred during service creation")
