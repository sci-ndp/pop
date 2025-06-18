# api/routes/register_routes/__init__.py

from fastapi import APIRouter

from .post_kafka import router as post_kafka_datasoruce_router
from .post_organization import router as post_organization_router
from .post_s3 import router as post_s3_router
from .post_service import router as post_service_router
from .post_url import router as post_url_router

router = APIRouter()

router.include_router(post_kafka_datasoruce_router)
router.include_router(post_organization_router)
router.include_router(post_url_router)
router.include_router(post_s3_router)
router.include_router(post_service_router)
