from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.claims.router import router as claims_router
from app.config import settings
from app.exceptions import AppException, app_exception_handler
from app.items.router import router as items_router
from app.matching.router import router as matching_router
from app.middleware.cors import setup_cors
from app.notifications.router import router as notifications_router
from app.search.router import router as search_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title="Lost & Found Platform",
        description="API for reporting lost and found items with secure claim verification",
        version="0.1.0",
        lifespan=lifespan,
    )

    setup_cors(app, settings)
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]

    # Register routers under /api/v1 prefix
    api_prefix = "/api/v1"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(items_router, prefix=api_prefix)
    app.include_router(search_router, prefix=api_prefix)
    app.include_router(matching_router, prefix=api_prefix)
    app.include_router(claims_router, prefix=api_prefix)
    app.include_router(notifications_router, prefix=api_prefix)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
