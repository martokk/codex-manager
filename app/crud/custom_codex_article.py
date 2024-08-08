from sqlmodel import Session

from app import models

from .base import BaseCRUD


class CustomCodexArticleCRUD(
    BaseCRUD[
        models.CustomCodexArticle, models.CustomCodexArticleCreate, models.CustomCodexArticleUpdate
    ]
):
    async def get_multi_by_codex_id(
        self, db: Session, *, codex_id: str, skip: int = 0, limit: int = 100
    ) -> list[models.CustomCodexArticle]:
        return await self.get_multi(db=db, codex_id=codex_id, skip=skip, limit=limit)

    async def get_multi_by_article_id(
        self, db: Session, *, article_id: str, skip: int = 0, limit: int = 100
    ) -> list[models.CustomCodexArticle]:
        return await self.get_multi(db=db, article_id=article_id, skip=skip, limit=limit)


custom_codex_article = CustomCodexArticleCRUD(models.CustomCodexArticle)
