from typing import List, Optional
from api.config.ckan_settings import ckan_settings


def list_organization(name: Optional[str] = None) -> List[str]:
    """
    Retrieve a list of all organizations, optionally filtered by name.

    Parameters
    ----------
    name : Optional[str]
        A string to filter organizations by name (case-insensitive).

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
    ckan = ckan_settings.ckan

    try:
        organizations = ckan.action.organization_list()

        # If a name is provided, filter the organizations list
        if name:
            name = name.lower()  # Make it case-insensitive
            organizations = [
                org for org in organizations if name in org.lower()]

        return organizations

    except Exception as e:
        raise Exception(f"Error retrieving list of organizations: {str(e)}")
