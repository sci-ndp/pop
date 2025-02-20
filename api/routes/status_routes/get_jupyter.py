# api\routes\status_routes\get_jupyter.py

from fastapi import APIRouter, HTTPException
from api.config.swagger_settings import swagger_settings


router = APIRouter()


@router.get(
    "/jupyter",
    summary="Get jupyter connection details",
    description=("Returns the the URL where the JupyterHub."),
)
async def get_jupyter_details():
    """
    Endpoint to retrieve jupyter connection details.

    Returns
    -------
    dict
        A dictionary containing the Jupyter URL.

    Raises
    ------
    HTTPException
        If there is an error retrieving Kafka details, an HTTPException
        is raised with a 500 status code.
    """
    try:
        return {"jupyter_url": swagger_settings.jupyter_url}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving Kafka details: {str(e)}")
