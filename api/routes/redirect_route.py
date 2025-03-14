# api/routes/redirect_service.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from api.config.swagger_settings import swagger_settings


router = APIRouter()

# Dictionary mapping service names to URLs
SERVICE_URLS = {
    "dashboard": "http://example.com/dashboard",
    "documentation": "http://example.com/docs",
    # Add more services as needed
}


@router.get(
    "/redirect/{service_name}",
    summary="Redirect to external service",
    description=(
        "Redirects user requests to external URLs based"
        " on the provided service name."),
)
async def redirect_to_service(service_name: str):
    """
    Redirects the request to a predefined external URL based on the given
    service name.

    Parameters:
    ----------
    service_name : str
        The name of the service to redirect to.

    Raises:
        HTTPException: 404 if the service name is not found.

    Returns:
        RedirectResponse: HTTP redirect response to the service URL.
    """
    if service_name == "jupyter":
        if swagger_settings.use_jupyterlab:
            return RedirectResponse(url=swagger_settings.jupyter_url)
        else:
            raise HTTPException(
                status_code=404,
                detail="Service 'jupyter' is currently disabled."
            )

    url = SERVICE_URLS.get(service_name)
    if not url:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found."
        )
    return RedirectResponse(url=url)
