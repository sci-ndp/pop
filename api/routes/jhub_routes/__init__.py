from fastapi import APIRouter
from .post_jupyterhub import router as post_jupyterhub_router

router = APIRouter()

router.include_router(post_jupyterhub_router)
