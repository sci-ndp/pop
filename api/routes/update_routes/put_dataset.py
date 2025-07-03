# api/routes/update_routes/put_dataset.py

from fastapi import APIRouter, Depends, HTTPException, Query

from api.config.ckan_settings import ckan_settings
from api.models.update_dataset_model import DatasetUpdateRequest
from api.services.keycloak_services.get_current_user import get_current_user
from api.services.url_services.update_dataset import update_dataset

router = APIRouter()


@router.put("/dataset/{dataset_id}", response_model=dict)
async def update_dataset_endpoint(
    dataset_id: str,
    data: DatasetUpdateRequest,
    server: str = Query("local", enum=["local", "pre_ckan"]),
    _: dict = Depends(get_current_user),
):
    try:
        ckan_instance = (
            ckan_settings.pre_ckan if server == "pre_ckan" else ckan_settings.ckan
        )
        return await update_dataset(
            dataset_id=dataset_id, data=data, ckan_instance=ckan_instance
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
