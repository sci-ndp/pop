# api/services/organization_services/create_organization.py
from typing import Literal, Optional

from ckanapi import NotFound, ValidationError

from api.config.ckan_settings import ckan_settings


def create_organization(
    name: str,
    title: str,
    description: Optional[str] = None,
    server: Literal["local", "pre_ckan"] = "local",
) -> str:
    """
    Create a new organization in CKAN.

    Parameters
    ----------
    name : str
        The name of the organization.
    title : str
        The title of the organization.
    description : Optional[str]
        The description of the organization.
    server : Literal["local", "pre_ckan"]
        The server instance where the organization will be created.
        Defaults to "local".

    Returns
    -------
    str
        The ID of the created organization.

    Raises
    ------
    Exception
        If there is an error creating the organization.
    """
    # Select CKAN instance based on 'server' parameter
    if server == "pre_ckan":
        if not ckan_settings.pre_ckan_enabled:
            raise Exception("Pre-CKAN is disabled and cannot be used.")
        ckan = ckan_settings.pre_ckan
    else:
        if not ckan_settings.ckan_local_enabled:
            raise Exception("Local CKAN is disabled and cannot be used.")
        ckan = ckan_settings.ckan

    try:
        # Create the organization in CKAN
        organization = ckan.action.organization_create(
            name=name, title=title, description=description
        )
        # Return the organization ID
        return organization["id"]
    except ValidationError as e:
        raise Exception(f"Validation error: {e.error_dict}")
    except NotFound:
        raise Exception("CKAN API endpoint not found")
    except Exception as e:
        if "Group name already exists in database" in str(e):
            raise Exception("Group name already exists in database")
        raise Exception(f"Error creating organization: {str(e)}")
