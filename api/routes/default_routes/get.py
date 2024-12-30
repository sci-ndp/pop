# api/routes/default_routes/get.py

from fastapi import APIRouter, Request
from api.services import default_services

router = APIRouter()


@router.get("/")
async def index(request: Request):
    return default_services.index(request)
