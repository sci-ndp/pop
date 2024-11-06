import json
from typing import Any, Dict, Optional

from api.config.ckan_settings import ckan_settings
import logging

logger = logging.getLogger(__name__)
# Define a set of reserved keys that should not be used in the extras
RESERVED_KEYS = {
    'name', 'title', 'owner_org', 'notes', 'id', 'resources',
    'collection', 'url', 'file_type'}


async def update_url(
    resource_id: str,
    resource_name: Optional[str] = None,
    resource_title: Optional[str] = None,
    owner_org: Optional[str] = None,
    resource_url: Optional[str] = None,
    file_type: Optional[str] = None,
    notes: Optional[str] = None,
    extras: Optional[Dict[str, str]] = None,
):
    ckan = ckan_settings.ckan

    # Fetch the existing resource data
    try:
        resource = ckan.action.package_show(id=resource_id)
    except Exception as e:
        raise Exception(
            f"Error fetching resource with ID {resource_id}: {str(e)}")

    # Extract current file type and processing from the resource
    current_extras = {
        extra['key']: extra['value'] for extra in resource.get('extras', [])}
    current_file_type = current_extras.get("file_type") 

    # Preserve existing resource fields
    updated_data = {
        'name': resource_name or resource['name'],
        'title': resource_title or resource['title'],
        'owner_org': owner_org or resource['owner_org'],
        'notes': notes or resource['notes'],
        'resources': resource['resources'],  # Preserve the existing resources
        'extras': resource.get('extras', [])  # Keep existing extras
    }

    # Merge new extras with existing extras, ensuring no data loss
    if extras:
        if RESERVED_KEYS.intersection(extras):
            raise KeyError(
                "Extras contain reserved keys: "
                f"{RESERVED_KEYS.intersection(extras)}")
        current_extras.update(extras)

    # Update the extras with new mapping, processing, and file type if provided
    if file_type:
        current_extras['file_type'] = file_type
    # Convert the merged extras back to CKAN format
    updated_data['extras'] = [
        {'key': k, 'value': v} for k, v in current_extras.items()]

    # Perform the update
    try:
        ckan.action.package_update(id=resource_id, **updated_data)

        # Update the resource URL if it has changed
        if resource_url:
            for res in resource['resources']:
                if res['format'].lower() == 'url':
                    ckan.action.resource_update(
                        id=res['id'], url=resource_url, package_id=resource_id)
                    break
    except Exception as e:
        raise Exception(
            f"Error updating resource with ID {resource_id}: {str(e)}")

    return {"message": "Resource updated successfully"}
