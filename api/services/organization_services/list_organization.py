# api/services/organization_services/list_organization.py
from typing import List, Optional

from api.config.ckan_settings import ckan_settings


def list_organization(name: Optional[str] = None, server: str = "global") -> List[str]:
    """
    Retrieve a list of all organizations from the specified CKAN server,
    optionally filtered by name.

    Parameters
    ----------
    name : Optional[str]
        A string to filter organizations by name (case-insensitive).
    server : str
        The CKAN server to use. Can be 'local', 'global', or 'pre_ckan'.
        Defaults to 'global'.

    Returns
    -------
    List[str]
        A list of organization names, filtered by the optional name if
        provided.

    Raises
    ------
    Exception
        If there is an error retrieving the list of organizations.
    """

    # Choose the CKAN instance based on 'server'
    if server == "pre_ckan":
        ckan_instance = ckan_settings.pre_ckan
    elif server == "global":
        ckan_instance = ckan_settings.ckan_global
    else:
        # Default to local if server is 'local' or unrecognized
        ckan_instance = ckan_settings.ckan_no_api_key

    try:
        organizations = ckan_instance.action.organization_list()

        # Filter the organizations if a name is provided
        if name:
            name_lower = name.lower()
            organizations = [org for org in organizations if name_lower in org.lower()]

        return organizations

    except Exception as exc:
        raise Exception(f"Error retrieving list of organizations: {str(exc)}")
