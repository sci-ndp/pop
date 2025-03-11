# api/routes/status_routes/__init__.py

from fastapi import APIRouter

from .get import router as get_router
from .kafka_details import router as kafka_router
from .get_jupyter import router as get_jupyter_router
from ...config.swagger_settings import swagger_settings

router = APIRouter()

router.include_router(get_router)
router.include_router(kafka_router)
if swagger_settings.use_jupyterlab:
    router.include_router(get_jupyter_router)
