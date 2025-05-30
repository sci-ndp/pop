# api\services\validation_services\validate_preckan_fields.py
from typing import Dict, List, Any


REQUIRED_CKAN_FIELDS = [
    'title',
    'notes',
    'tags',
    'extras:uploadType',
    'extras:dataType',
    'extras:purpose',
    'extras:publisherName',
    'extras:publisherEmail',
    'extras:creatorName',
    'extras:creatorEmail',
    'extras:pocName',
    'extras:pocEmail',
    'extras:license_or_otherLicense',  # Changed for better handling
    'extras:issueDate',
    'extras:lastUpdateDate',
    'resource:name',
    'resource:description',
    'resource:mimetype',
    'resource:status',
]


def validate_preckan_fields(document: Dict[str, Any]) -> List[str]:
    """
    Validate that a document has all required CKAN fields for insertion into
    preckan.

    Args:
        document (Dict): The document to validate.

    Returns:
        List[str]: A list of missing required fields.
            Empty if none are missing.
    """
    missing_fields = []

    for field in REQUIRED_CKAN_FIELDS:
        if field.startswith('extras:'):
            # Handle extras fields
            key = field.split(':', 1)[1]
            if key == 'license_or_otherLicense':
                if 'extras' not in document or not (
                    'license' in document['extras'] or 'otherLicense' in document['extras']
                ):
                    missing_fields.append('extras:license / extras:otherLicense')
            elif 'extras' not in document or key not in document['extras']:
                missing_fields.append(field)
        elif field.startswith('resource:'):
            # Handle resource fields (assuming a single resource for simplicity, if multiple, iterate)
            if 'resources' not in document or not document['resources']:
                missing_fields.append(field)
                continue

            resource_found = False
            for resource in document['resources']:
                subfield = field.split(':', 1)[1]
                if subfield in resource:
                    resource_found = True
                    break
            if not resource_found:
                missing_fields.append(field)
        else:
            # Handle top-level fields like 'title', 'notes', 'tags'
            if field not in document:
                missing_fields.append(field)

    return missing_fields
