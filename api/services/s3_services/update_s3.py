# api/services/s3_services/update_s3.py

from typing import Dict, Optional

from api.config.ckan_settings import ckan_settings

RESERVED_KEYS = {"name", "title", "owner_org", "notes", "id", "resources", "collection"}


async def update_s3(
    resource_id: str,
    resource_name: Optional[str] = None,
    resource_title: Optional[str] = None,
    owner_org: Optional[str] = None,
    resource_s3: Optional[str] = None,
    notes: Optional[str] = None,
    extras: Optional[Dict[str, str]] = None,
    ckan_instance=None,  # new optional parameter
):
    """
    Update an existing S3 resource in CKAN, supporting a custom ckan_instance.
    If ckan_instance is None, defaults to ckan_settings.ckan.
    """
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    try:
        # Fetch the existing resource
        resource = ckan_instance.action.package_show(id=resource_id)
    except Exception as e:
        raise Exception(f"Error fetching S3 resource: {str(e)}")

    # Preserve all existing fields unless new values are provided
    resource["name"] = resource_name or resource.get("name")
    resource["title"] = resource_title or resource.get("title")
    resource["owner_org"] = owner_org or resource.get("owner_org")
    resource["notes"] = notes or resource.get("notes")

    # Handle extras update by merging current extras with new ones
    current_extras = {
        extra["key"]: extra["value"] for extra in resource.get("extras", [])
    }

    if extras:
        if RESERVED_KEYS.intersection(extras):
            raise KeyError(
                "Extras contain reserved keys: " f"{RESERVED_KEYS.intersection(extras)}"
            )
        current_extras.update(extras)

    resource["extras"] = [{"key": k, "value": v} for k, v in current_extras.items()]

    try:
        # Update the resource package in CKAN
        updated_resource = ckan_instance.action.package_update(**resource)

        # If the S3 URL is updated, update the corresponding resource
        if resource_s3:
            for res in resource["resources"]:
                if res["format"].lower() == "s3":
                    ckan_instance.action.resource_update(
                        id=res["id"], url=resource_s3, package_id=resource_id
                    )
                    break
    except Exception as e:
        raise Exception(f"Error updating S3 resource: {str(e)}")

    return updated_resource["id"]
