# api/services/datasource_services/search_datasets_by_terms.py

import json
import re
from typing import List, Optional, Literal
from fastapi import HTTPException
from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings
from api.models import DataSourceResponse, Resource


def escape_solr_special_chars(value: str) -> str:
    pattern = re.compile(r'([+\-\!\(\)\{\}\[\]\^"~\*\?:\\])')
    return pattern.sub(r'\\\1', value)


async def search_datasets_by_terms(
    terms_list: List[str],
    keys_list: Optional[List[Optional[str]]] = None,
    server: Literal['local', 'global', 'pre_ckan'] = "local"
) -> List[DataSourceResponse]:
    if server not in ["local", "global", "pre_ckan"]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid server specified. Use 'local', "
                "'global', or 'pre_ckan'.")
        )

    if server == "local":
        ckan = ckan_settings.ckan_no_api_key
    elif server == "global":
        ckan = ckan_settings.ckan_global
    elif server == "pre_ckan":
        ckan = ckan_settings.pre_ckan_no_api_key

    escaped_terms = [escape_solr_special_chars(term) for term in terms_list]

    query_parts = []

    if keys_list:
        processed_keys = [
            None if key is None or key.lower() == 'null' else key
            for key in keys_list
        ]

        for term, key in zip(escaped_terms, processed_keys):
            if key:
                escaped_key = escape_solr_special_chars(key)
                query_parts.append(f"{escaped_key}:{term}")
            else:
                query_parts.append(term)
    else:
        query_parts = escaped_terms

    query_string = ' AND '.join(query_parts)

    try:
        datasets = ckan.action.package_search(q=query_string, rows=1000)
        results_list = []

        for dataset in datasets['results']:
            dataset_str = json.dumps(dataset).lower()

            if all(term.lower() in dataset_str for term in terms_list):
                resources_list = [
                    Resource(
                        id=res['id'],
                        url=res['url'],
                        name=res['name'],
                        description=res.get('description'),
                        format=res.get('format')
                    )
                    for res in dataset.get('resources', [])
                ]

                organization_name = dataset.get(
                    'organization', {}).get('name') \
                    if dataset.get('organization') else None

                extras = {
                    extra['key']: extra['value']
                    for extra in dataset.get('extras', [])
                }

                if 'mapping' in extras:
                    try:
                        extras['mapping'] = json.loads(extras['mapping'])
                    except json.JSONDecodeError:
                        pass

                if 'processing' in extras:
                    try:
                        extras['processing'] = json.loads(extras['processing'])
                    except json.JSONDecodeError:
                        pass

                results_list.append(
                    DataSourceResponse(
                        id=dataset['id'],
                        name=dataset['name'],
                        title=dataset['title'],
                        owner_org=organization_name,
                        description=dataset.get('notes'),
                        resources=resources_list,
                        extras=extras
                    )
                )

        return results_list

    except NotFound:
        return []

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error searching for datasets: {str(e)}"
        )
