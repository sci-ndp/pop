from fastapi import APIRouter

from .post_dspaces_route import router as post_dspaces_router
from .delete_dspaces import router as delete_dspaces_router

router = APIRouter()

router.include_router(post_dspaces_router)
router.include_router(delete_dspaces_router)
