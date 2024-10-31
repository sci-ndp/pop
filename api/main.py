import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api.routes as routes
from api.config import swagger_settings


app = FastAPI(
    title=swagger_settings.swagger_title,
    description=swagger_settings.swagger_description,
    version=swagger_settings.swagger_version,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(routes.default_router, include_in_schema=False)
app.include_router(routes.register_router, tags=["Registration"])
app.include_router(routes.search_router, tags=["Search"])
app.include_router(routes.update_router, tags=["Update"])
app.include_router(routes.delete_router, tags=["Delete"])
app.include_router(routes.token_router, tags=["Token"])
app.include_router(routes.status_router, prefix="/status", tags=["Status"])


logger = logging.getLogger(__name__)
