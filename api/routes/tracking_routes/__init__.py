# api/routes/tracking_routes/__init__.py

from fastapi import APIRouter

from .get_tracking_status import router as get_tracking_status_router

router = APIRouter()

router.include_router(get_tracking_status_router)
