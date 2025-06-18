# api/services/dataset_services/delete_dataset.py
from ckanapi import NotFound

from api.config.ckan_settings import ckan_settings


def delete_dataset(
    dataset_name: str = None, resource_id: str = None, ckan_instance=None
):
    """
    Delete a dataset from CKAN by its name or resource_id, allowing
    a custom CKAN instance. Defaults to ckan_settings.ckan if none is
    provided.
    """
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    if not (dataset_name or resource_id):
        raise ValueError("Must provide either dataset_name or resource_id.")

    try:
        # Retrieve the dataset to ensure it exists
        if dataset_name:
            dataset = ckan_instance.action.package_show(id=dataset_name)
            if resource_id and resource_id != dataset["id"]:
                raise ValueError(
                    f"Provided resource_id '{resource_id}' does not match "
                    f"the dataset id '{dataset['id']}' for '{dataset_name}'."
                )
            resource_id = dataset["id"]

        # Attempt to delete the dataset using its ID
        ckan_instance.action.dataset_purge(id=resource_id)

    except NotFound:
        raise Exception(f"Dataset '{dataset_name}' not found.")
    except Exception as e:
        raise Exception(f"Error deleting dataset '{dataset_name}': {str(e)}")
