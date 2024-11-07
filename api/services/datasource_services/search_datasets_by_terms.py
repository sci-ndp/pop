import json
from typing import List, Optional
from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings
from api.models import DataSourceResponse, Resource


async def search_datasets_by_terms(
    terms_list: List[str],
    server: Optional[str] = "local"
) -> List[DataSourceResponse]:
    """
    Search for datasets in CKAN that match the given list of terms.

    This function queries the CKAN API to find datasets that contain all the
    specified terms in any of their fields.

    Args:
        terms_list (List[str]): A list of terms to search for.
        server (Optional[str], optional): The CKAN server to use ("local" or
            "global"). Defaults to "local".

    Returns:
        List[DataSourceResponse]: A list of datasets matching the search terms.

    Raises:
        Exception: If an invalid server is specified or if there is an error
            during the search.
    """
    if server not in ["local", "global"]:
        raise Exception(
            "Invalid server specified. Please specify 'local' or 'global'."
        )

    if server == "local":
        ckan = ckan_settings.ckan_no_api_key  # Use the no API key instance
    elif server == "global":
        ckan = ckan_settings.ckan_global

    # Build the query string by joining terms with ' AND '
    # To match any of the terms, use ' OR ' instead
    query_string = ' AND '.join(terms_list)

    try:
        # Search for datasets matching the query
        datasets = ckan.action.package_search(q=query_string, rows=1000)
        results_list = []

        for dataset in datasets['results']:
            resources_list = [
                Resource(
                    id=res['id'],
                    url=res['url'],
                    name=res['name'],
                    description=res.get('description'),
                    format=res.get('format')
                ) for res in dataset.get('resources', [])
            ]

            organization_name = dataset.get('organization', {}).get('name') \
                if dataset.get('organization') else None
            extras = {
                extra['key']: extra['value']
                for extra in dataset.get('extras', [])
            }

            # Parse JSON strings for specific extras
            if 'mapping' in extras:
                extras['mapping'] = json.loads(extras['mapping'])
            if 'processing' in extras:
                extras['processing'] = json.loads(extras['processing'])

            results_list.append(DataSourceResponse(
                id=dataset['id'],
                name=dataset['name'],
                title=dataset['title'],
                owner_org=organization_name,
                description=dataset.get('notes'),
                resources=resources_list,
                extras=extras
            ))

        return results_list

    except NotFound:
        return []
    except Exception as e:
        raise Exception(f"Error searching for datasets: {str(e)}")
