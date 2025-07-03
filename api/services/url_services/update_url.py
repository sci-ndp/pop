# api/services/url_services/update_url.py

import json
import logging
from typing import Any, Dict, Optional

from api.config.ckan_settings import ckan_settings

logger = logging.getLogger(__name__)

RESERVED_KEYS = {
    "name",
    "title",
    "owner_org",
    "notes",
    "id",
    "resources",
    "collection",
    "url",
    "mapping",
    "processing",
    "file_type",
}


async def update_url(
    resource_id: str,
    resource_name: Optional[str] = None,
    resource_title: Optional[str] = None,
    owner_org: Optional[str] = None,
    resource_url: Optional[str] = None,
    file_type: Optional[str] = None,
    notes: Optional[str] = None,
    extras: Optional[Dict[str, str]] = None,
    mapping: Optional[Dict[str, str]] = None,
    processing: Optional[Dict[str, Any]] = None,
    ckan_instance=None,  # new optional param for server selection
):
    """
    Update an existing URL resource in CKAN, allowing a custom ckan_instance.
    If ckan_instance is None, defaults to ckan_settings.ckan.
    """

    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    # Fetch the existing resource data
    try:
        resource = ckan_instance.action.package_show(id=resource_id)
    except Exception as e:
        raise Exception(f"Error fetching resource with ID {resource_id}: {str(e)}")

    # Extract current file type and processing from the resource
    current_extras = {
        extra["key"]: extra["value"] for extra in resource.get("extras", [])
    }
    current_file_type = current_extras.get("file_type")
    current_processing = json.loads(current_extras.get("processing", "{}"))

    # Validate or update the processing info if the file type changes
    if file_type and file_type != current_file_type:
        if processing is not None:
            processing = validate_manual_processing_info(file_type, processing)
        else:
            processing = validate_manual_processing_info(file_type, current_processing)
    elif processing is not None:
        processing = validate_manual_processing_info(current_file_type, processing)

    # Preserve existing resource fields
    updated_data = {
        "name": resource_name or resource["name"],
        "title": resource_title or resource["title"],
        "owner_org": owner_org or resource["owner_org"],
        "notes": notes or resource["notes"],
        "resources": resource["resources"],
        "extras": resource.get("extras", []),
    }

    # Merge new extras with existing extras
    if extras:
        if RESERVED_KEYS.intersection(extras):
            raise KeyError(
                "Extras contain reserved keys: " f"{RESERVED_KEYS.intersection(extras)}"
            )
        current_extras.update(extras)

    # Update extras with new mapping, processing, file_type if provided
    if file_type:
        current_extras["file_type"] = file_type
    if mapping:
        current_extras["mapping"] = json.dumps(mapping)
    if processing is not None:
        current_extras["processing"] = json.dumps(processing)

    updated_data["extras"] = [{"key": k, "value": v} for k, v in current_extras.items()]

    # Perform the update
    try:
        ckan_instance.action.package_update(id=resource_id, **updated_data)

        # Update the resource URL if it has changed
        if resource_url:
            for res in resource["resources"]:
                if res["format"].lower() == "url":
                    ckan_instance.action.resource_update(
                        id=res["id"], url=resource_url, package_id=resource_id
                    )
                    break
    except Exception as e:
        raise Exception(f"Error updating resource with ID {resource_id}: {str(e)}")

    return {"message": "Resource updated successfully"}


def validate_manual_processing_info(file_type: str, processing: dict):
    """
    Manually validate the processing information based on the file type.
    """
    expected_fields = {
        "stream": {"refresh_rate", "data_key"},
        "CSV": {"delimiter", "header_line", "start_line", "comment_char"},
        "TXT": {"delimiter", "header_line", "start_line"},
        "JSON": {"info_key", "additional_key", "data_key"},
        "NetCDF": {"group"},
    }
    required_fields = {
        "CSV": {"delimiter", "header_line", "start_line"},
        "TXT": {"delimiter", "header_line", "start_line"},
    }

    expected = expected_fields.get(file_type)
    required = required_fields.get(file_type, set())

    unexpected_fields = set(processing.keys()) - (expected or set())
    if unexpected_fields:
        raise ValueError(
            f"Unexpected fields in processing for {file_type}: " f"{unexpected_fields}"
        )

    missing_required_fields = required - set(processing.keys())
    if missing_required_fields:
        raise ValueError(
            f"Missing required fields in processing for {file_type}: "
            f"{missing_required_fields}"
        )

    return processing
