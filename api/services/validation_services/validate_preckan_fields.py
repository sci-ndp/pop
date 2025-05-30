from typing import Dict, List, Any

# Adjust REQUIRED_CKAN_FIELDS to reflect the keys in your incoming payload
# and what validate_preckan_fields expects after data.dict()
REQUIRED_CKAN_FIELDS = [
    'title',            # Maps to data.title or data.resource_title in your payload
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
    'extras:license_or_otherLicense', # Special handling for license/otherLicense
    'extras:issueDate',
    'extras:lastUpdateDate',
    'resource:name',        # Maps to data.resource.name
    'resource:description', # Maps to data.resource.description
    'resource:mimetype',    # Maps to data.resource.mimetype
    'resource:status',      # Maps to data.resource.status
]


def validate_preckan_fields(document: Dict[str, Any]) -> List[str]:
    """
    Validate that a document has all required CKAN fields for insertion into
    preckan, adapted for your incoming payload structure.

    Args:
        document (Dict): The document (payload from data.dict()) to validate.

    Returns:
        List[str]: A list of missing required fields.
                   Empty if none are missing.
    """
    missing_fields = []

    # Map your payload's keys to the generic CKAN field names for validation
    # This dictionary helps translate where the validator should look
    key_mapping = {
        'title': 'title', # Your payload has a top-level 'title' which should be fine for this
        'notes': 'notes',
        'tags': 'tags',
        'extras': 'extras',
        'resource': 'resource' # Assuming 'resource' is a top-level dict in your payload
    }

    for field in REQUIRED_CKAN_FIELDS:
        if field.startswith('extras:'):
            key = field.split(':', 1)[1]
            if key == 'license_or_otherLicense':
                # Check for either 'license_id' OR 'otherLicense' within 'extras' or at top-level
                # Based on your example, 'license_id' is top-level and 'otherLicense' is in 'extras'
                if ('license_id' not in document or not document['license_id']) and \
                   ('extras' not in document or 'otherLicense' not in document['extras'] or not document['extras']['otherLicense']):
                    missing_fields.append('license_id / extras:otherLicense')
            elif 'extras' not in document or key not in document['extras'] or not document['extras'][key]:
                # Check if the 'extras' dict exists and the specific key is present and not empty
                missing_fields.append(field)

        elif field.startswith('resource:'):
            # Handle resource fields, expecting a direct 'resource' dictionary in the payload
            subfield = field.split(':', 1)[1]
            # Check if 'resource' dict exists and if the subfield is in it and not empty
            if 'resource' not in document or subfield not in document['resource'] or not document['resource'][subfield]:
                missing_fields.append(field)
        else:
            # Handle top-level fields like 'title', 'notes', 'tags'
            # We'll check if the corresponding mapped key exists and is not empty
            actual_key = key_mapping.get(field, field) # Use mapping if available, else field itself
            if actual_key not in document or not document[actual_key]:
                missing_fields.append(field)

    return missing_fields
