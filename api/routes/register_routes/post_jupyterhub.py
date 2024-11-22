from fastapi import APIRouter, HTTPException
from api.services.jupyterhub_services.run_jupyterhub import run_jupyterhub

router = APIRouter()

@router.post("/jupyterhub")
def create_jupyterhub_route():
    """
    Start a JupyterHub instance using the preconfigured setup.
    :return: Success message or error.
    """
    try:
        result = run_jupyterhub()
        return result
    except HTTPException as e:
        raise e