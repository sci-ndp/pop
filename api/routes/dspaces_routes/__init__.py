from fastapi import APIRouter

from .post_dspaces_route import router as post_dspaces_router

router = APIRouter()

router.include_router(post_dspaces_router)