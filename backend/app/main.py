"""FastAPI Application Entrypoint for OSINT-X."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.models  # Pre-import all authoritative models
from app.api import api_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.database import async_engine
from app.core.exceptions import OSINTXException
from app.core.logging import logger, setup_logging
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown event management."""
    setup_logging(
        log_level="DEBUG" if settings.APP_DEBUG else "INFO",
        app_env=settings.APP_ENV,
    )
    logger.info(
        "Starting %s v%s in %s mode",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
    )

    # Initialize PostgreSQL tables automatically if they do not exist
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema verified and synchronized.")
    except Exception as exc:
        logger.warning("Database schema initialization warning: %s", str(exc))

    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_application() -> FastAPI:
    """Factory function for FastAPI application instance."""
    app = FastAPI(
        title=f"{settings.APP_NAME} Intelligence API",
        description="Defensive Cybersecurity Intelligence & Attack-Surface Platform",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Exception Handlers
    @app.exception_handler(OSINTXException)
    async def osintx_exception_handler(request: Request, exc: OSINTXException) -> JSONResponse:
        logger.warning("Domain exception on %s %s: %s", request.method, request.url.path, exc.message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected internal error occurred.",
            },
        )

    # Direct top-level health endpoint for Docker / orchestration probes
    app.include_router(health_router, prefix="/api")

    # Versioned API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
