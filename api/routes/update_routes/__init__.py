from fastapi import APIRouter

from .patch_general_dataset import router as patch_general_dataset
from .put_general_dataset import router as put_general_dataset
from .put_kafka import router as put_kafka
from .put_s3 import router as put_s3
from .put_url import router as put_url

router = APIRouter()

router.include_router(put_kafka)
router.include_router(put_url)
router.include_router(put_s3)
router.include_router(put_general_dataset)
router.include_router(patch_general_dataset)
