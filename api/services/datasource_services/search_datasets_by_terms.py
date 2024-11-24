import json
from typing import List, Optional, Literal
from ckanapi import NotFound
from fastapi import HTTPException
from api.config.ckan_settings import ckan_settings
from api.models import DataSourceResponse, Resource


async def search_datasets_by_terms(
    terms_list: List[str],
    keys_list: Optional[List[Optional[str]]] = None,
    server: Literal['local', 'global'] = "local"
) -> List[DataSourceResponse]:
    """
    Search for datasets in CKAN that match the given list of terms with
    optional key specifications.

    Args:
        terms_list (List[str]): A list of terms to search for.
        keys_list (Optional[List[Optional[str]]]): A list specifying the keys
        for each term.
            Use `None` for global search of the term.
        server (Literal['local', 'global'], optional): The CKAN server to use
        ("local" or "global").
            Defaults to "local".

    Returns:
        List[DataSourceResponse]: A list of datasets matching the search terms.

    Raises:
        HTTPException: If there is an error during the search.
    """
    if server not in ["local", "global"]:
        # This check is redundant now as FastAPI handles it, but keeping for
        # extra safety
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid server specified. Please specify "
                "'local' or 'global'.")
        )

    if server == "local":
        ckan = ckan_settings.ckan_no_api_key  # Use the no API key instance
    else:
        ckan = ckan_settings.ckan_global

    # Build the query string based on terms and keys
    query_parts = []
    if keys_list:
        # Convert 'null' strings to None
        processed_keys = [
            None if key is None or key.lower() == 'null' else key
            for key in keys_list]
        for term, key in zip(terms_list, processed_keys):
            if key:
                query_parts.append(f"{key}:{term}")
            else:
                query_parts.append(term)
    else:
        # Existing behavior: search all terms globally
        query_parts = terms_list

    # Join query parts with ' AND ' to ensure all terms are matched
    query_string = ' AND '.join(query_parts)

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
                try:
                    extras['mapping'] = json.loads(extras['mapping'])
                except json.JSONDecodeError:
                    pass  # Handle or log as needed
            if 'processing' in extras:
                try:
                    extras['processing'] = json.loads(extras['processing'])
                except json.JSONDecodeError:
                    pass  # Handle or log as needed

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
        raise HTTPException(status_code=400,
                            detail=f"Error searching for datasets: {str(e)}")
