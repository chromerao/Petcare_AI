import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from docqa.api.routes.health import router as health_router
from docqa.api.routes.query import router as query_router
from docqa.api.routes.sources import router as sources_router
from docqa.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    application.include_router(health_router, prefix="/api/v1")
    application.include_router(query_router, prefix="/api/v1")
    application.include_router(sources_router, prefix="/api/v1")
    return application


app = create_app()


def run() -> None:
    uvicorn.run("docqa.api.main:app", host="127.0.0.1", port=8000, reload=True)
