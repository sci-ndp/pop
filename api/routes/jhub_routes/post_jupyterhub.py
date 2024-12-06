import httpx
import requests
from fastapi.responses import Response, JSONResponse, HTMLResponse, PlainTextResponse
from fastapi import APIRouter, HTTPException, Request
from starlette.responses import RedirectResponse


router = APIRouter()


@router.api_route("/jupyterhub", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
@router.api_route("/jupyterhub/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_to_jupyterhub(request: Request, path: str = ""):
    """
    Proxy requests to the JupyterHub server, including static assets and other resources.
    """
    hub_url = f"http://jupyterhub:8002/{path}"

    # Extract headers from the original request, ensuring no duplicate Host header
    headers = {
        key: value for key, value in request.headers.items() if key.lower() != "host"
    }
    headers["X-Forwarded-For"] = request.client.host
    headers["X-Forwarded-Host"] = request.headers.get("host")
    headers["X-Forwarded-Proto"] = request.url.scheme

    try:
        # Create an HTTPX client for forwarding requests
        async with httpx.AsyncClient(follow_redirects=False) as client:
            # Forward the request dynamically based on the method
            response = await client.request(
                method=request.method,
                url=hub_url,
                headers=headers,
                params=request.query_params,
                content=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
            )

        # Rewrite redirects (Location header) to use the proxy base path
        if "Location" in response.headers:
            original_location = response.headers["Location"]
            if original_location.startswith("/"):
                rewritten_location = f"/jupyterhub{original_location}"
            elif original_location.startswith("http://jupyterhub:8002"):
                rewritten_location = original_location.replace("http://jupyterhub:8002", "/jupyterhub")
            else:
                rewritten_location = original_location  # No rewriting needed
            response.headers["Location"] = rewritten_location

        # Return the proxied response with appropriate headers and content
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("Content-Type", None),
        )

    except httpx.RequestError as exc:
        print(f"Error forwarding request to JupyterHub: {exc}")
        return JSONResponse({"error": "Unable to connect to JupyterHub"}, status_code=502)