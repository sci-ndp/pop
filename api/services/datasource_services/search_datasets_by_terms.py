# api/services/datasource_services/search_datasets_by_terms.py

import json
import re
from typing import List, Optional, Literal
from fastapi import HTTPException
from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings
from api.models import DataSourceResponse, Resource


def escape_solr_special_chars(value: str) -> str:
    """
    Escape special characters for Solr queries.

    According to Solr documentation, the following characters need to be
    escaped: + - && || ! ( ) { } [ ] ^ " ~ * ? : \\
    """
    # Compile a regex that matches any special character that Solr requires
    # escaping.
    pattern = re.compile(r'([+\-\!\(\)\{\}\[\]\^"~\*\?:\\])')
    # Replace each found character with a backslash-escaped version.
    return pattern.sub(r'\\\1', value)


async def search_datasets_by_terms(
    terms_list: List[str],
    keys_list: Optional[List[Optional[str]]] = None,
    server: Literal['local', 'global'] = "local"
) -> List[DataSourceResponse]:
    """
    Search for datasets in CKAN that match given terms with optional keys.

    Parameters
    ----------
    terms_list : List[str]
        A list of terms to be used in the search query.
    keys_list : Optional[List[Optional[str]]]
        An optional list of keys corresponding to each term. Use 'null' or
        None for a global search on that term.
    server : Literal['local', 'global']
        The CKAN server to use ('local' or 'global'). Defaults to 'local'.

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    HTTPException
        If there is an error during the search or if the server is invalid.
    """
    # Validate that server is either 'local' or 'global'.
    if server not in ["local", "global"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid server specified. Use 'local' or 'global'."
        )

    # Select the appropriate CKAN instance.
    if server == "local":
        ckan = ckan_settings.ckan_no_api_key
    else:
        ckan = ckan_settings.ckan_global

    # Escape all terms to avoid issues with special characters in Solr queries.
    escaped_terms = [escape_solr_special_chars(term) for term in terms_list]

    query_parts = []

    if keys_list:
        # Convert 'null' or None keys to None, indicating global search.
        processed_keys = [
            None if key is None or key.lower() == 'null' else key
            for key in keys_list
        ]

        # Combine keys and terms. If a key is provided, pair it with a term.
        # If key is None, the term is searched globally.
        for term, key in zip(escaped_terms, processed_keys):
            if key:
                escaped_key = escape_solr_special_chars(key)
                query_parts.append(f"{escaped_key}:{term}")
            else:
                query_parts.append(term)
    else:
        # If no keys are provided, all terms are considered global searches.
        query_parts = escaped_terms

    # Join query parts with 'AND' so that all terms must match.
    query_string = ' AND '.join(query_parts)

    try:
        # Execute the search query in CKAN.
        datasets = ckan.action.package_search(q=query_string, rows=1000)
        results_list = []

        # Process each returned dataset into the response model.
        for dataset in datasets['results']:
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

            organization_name = dataset.get('organization', {}).get('name') \
                if dataset.get('organization') else None

            extras = {
                extra['key']: extra['value']
                for extra in dataset.get('extras', [])
            }

            # Attempt to parse JSON in 'mapping' and 'processing' extras.
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
        # If no datasets match the query, return an empty list.
        return []

    except Exception as e:
        # If any other error occurs, raise an HTTPException with the error.
        raise HTTPException(
            status_code=400,
            detail=f"Error searching for datasets: {str(e)}"
        )
