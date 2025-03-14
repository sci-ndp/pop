# api/main.py

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from api.tasks.metrics_task import record_system_metrics
import asyncio

import api.routes as routes
from api.config import swagger_settings, ckan_settings


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run tasks on startup and handle shutdown."""
    task = asyncio.create_task(record_system_metrics())
    yield
    task.cancel()


app = FastAPI(
    title=swagger_settings.swagger_title,
    description=swagger_settings.swagger_description,
    version=swagger_settings.swagger_version,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routes.default_router, include_in_schema=False)
if ckan_settings.ckan_local_enabled:
    app.include_router(routes.register_router, tags=["Registration"])
app.include_router(routes.search_router, tags=["Search"])
if ckan_settings.ckan_local_enabled:
    app.include_router(routes.update_router, tags=["Update"])
if ckan_settings.ckan_local_enabled:
    app.include_router(routes.delete_router, tags=["Delete"])
app.include_router(routes.token_router, tags=["Token"])
app.include_router(routes.status_router, prefix="/status", tags=["Status"])
app.include_router(routes.redirect_router, tags=["Redirect"])


# Custom OpenAPI Schema for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def custom_openapi():
    """
    Customize the OpenAPI schema to support both username/password
    and token-based authentication.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Define security schemes for OAuth2 Password and Bearer Token
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2Password": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/token",
                    "scopes": {},
                }
            },
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply both security schemes globally to all endpoints
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [
                {"OAuth2Password": []},  # Username/password authentication
                {"BearerAuth": []},  # Token authentication
            ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set the custom OpenAPI schema
app.openapi = custom_openapi

# Configure logger
logger = logging.getLogger(__name__)
