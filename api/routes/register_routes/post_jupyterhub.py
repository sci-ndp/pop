from fastapi import APIRouter, HTTPException, Depends
from api.services.jupyterhub_services.run_jupyterhub import run_jupyterhub

router = APIRouter()

@router.post("/jupyterhub/start")
def create_jupyterhub_route(name: str, user_quota: int):
    """
    Start a JupyterHub instance using the preconfigured setup.
    :return: Success message or error.
    """
    try:
        result = run_jupyterhub(name, user_quota)
        return result
    except HTTPException as e:
        raise e