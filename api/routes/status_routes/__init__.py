# api/routes/status_routes/__init__.py

from fastapi import APIRouter

from .get import router as get_router
from .kafka_details import router as kafka_router

router = APIRouter()

router.include_router(get_router)
router.include_router(kafka_router)
