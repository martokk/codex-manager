from fastapi import APIRouter

from app.views.pages import (
    account,
    articles,
    login,
    root,
    user,
    reviews,
    custom_codex_articles,
    custom_codices,
)

views_router = APIRouter(include_in_schema=False)
views_router.include_router(root.router, tags=["Views"])
views_router.include_router(articles.router, tags=["Articles"])
views_router.include_router(login.router, tags=["Logins"])
views_router.include_router(account.router, prefix="/account", tags=["Account"])
views_router.include_router(user.router, prefix="/user", tags=["Users"])
views_router.include_router(custom_codices.router, tags=["Custom Codex"])
views_router.include_router(custom_codex_articles.router, tags=["Custom Codex Articles"])
views_router.include_router(reviews.router, tags=["Reviews"])
