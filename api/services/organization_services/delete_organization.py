# api/services/organization_services/delete_organization.py
from ckanapi import NotFound

from api.config.ckan_settings import ckan_settings


def delete_organization(
    organization_name: str, ckan_instance=None  # new optional parameter
):
    """
    Delete an organization from CKAN by its name, optionally using a
    custom ckan_instance. Defaults to ckan_settings.ckan if none is provided.
    """
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    try:
        # Retrieve the organization to ensure it exists
        organization = ckan_instance.action.organization_show(id=organization_name)
        organization_id = organization["id"]

        # Delete all datasets associated with the organization
        datasets = ckan_instance.action.package_search(
            fq=f"owner_org:{organization_id}", rows=1000
        )
        for dataset in datasets["results"]:
            ckan_instance.action.dataset_purge(id=dataset["id"])

        # Delete the organization
        ckan_instance.action.organization_delete(id=organization_id)
        ckan_instance.action.organization_purge(id=organization_id)

    except NotFound:
        raise Exception("Organization not found")
    except Exception as e:
        raise Exception(f"Error deleting organization: {str(e)}")
