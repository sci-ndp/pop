# api/services/url_services/update_dataset.py
from api.config import ckan_settings
from api.models.update_dataset_model import DatasetUpdateRequest


async def update_dataset(
    dataset_id: str, data: DatasetUpdateRequest, ckan_instance=None
):
    if ckan_instance is None:
        ckan_instance = ckan_settings.ckan

    try:
        dataset = ckan_instance.action.package_show(id=dataset_id)
    except Exception as e:
        raise Exception(f"Cannot fetch dataset {dataset_id}: {e}")

    existing_tags = {tag["name"] for tag in dataset.get("tags", [])}
    new_tags = set(data.tags or [])
    all_tags = [{"name": t} for t in existing_tags | new_tags]

    existing_groups = {group["name"] for group in dataset.get("groups", [])}
    new_groups = set(data.groups or [])
    all_groups = [{"name": g} for g in existing_groups | new_groups]

    existing_extras = {e["key"]: e["value"] for e in dataset.get("extras", [])}
    new_extras = data.extras or {}
    merged_extras = [
        {"key": k, "value": v} for k, v in {**existing_extras, **new_extras}.items()
    ]

    patch_fields = {
        "id": dataset_id,
        "title": data.title or dataset["title"],
        "notes": data.notes or dataset["notes"],
        "tags": all_tags,
        "groups": all_groups,
        "extras": merged_extras,
    }

    try:
        ckan_instance.action.package_patch(**patch_fields)
    except Exception as e:
        raise Exception(f"Failed to patch dataset {dataset_id}: {e}")

    if data.resources:
        for res in data.resources:
            try:
                ckan_instance.action.resource_create(
                    package_id=dataset_id,
                    url=res.resource_url,
                    format=res.format,
                    name=res.name,
                    description=res.description,
                )
            except Exception as e:
                raise Exception(f"Failed to add resource: {e}")

    return {"message": "Dataset updated successfully with additional resources."}
