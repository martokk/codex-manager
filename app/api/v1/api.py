from fastapi import APIRouter

from app import models, settings, version
from app.api.v1.endpoints import login, users, article

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/user", tags=["Users"])
api_router.include_router(article.router, prefix="/article", tags=["Articles"])


@api_router.get("/", response_model=models.HealthCheck, tags=["status"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict[str, str]: Health check response.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": version,
        "description": settings.PROJECT_DESCRIPTION,
    }
