# api\services\validation_services\validate_preckan_fields.py
from typing import Dict, List


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
    'extras:license / extras:otherLicense',
    'extras:issueDate',
    'extras:lastUpdateDate',
    'resource:name',
    'resource:description',
    'resource:mimetype',
    'resource:status',
]


def validate_preckan_fields(document: Dict) -> List[str]:
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
        # Handle nested fields if necessary
        if ':' in field:
            prefix, subfield = field.split(':', 1)
            if prefix not in document or subfield not in document[prefix]:
                missing_fields.append(field)
        else:
            if field not in document:
                missing_fields.append(field)

    return missing_fields
