from sqlmodel import Session

from app import models

from .base import BaseCRUD


class ReviewCRUD(BaseCRUD[models.Review, models.ReviewCreate, models.ReviewUpdate]):
    async def get_multi_by_article_id(
        self, db: Session, *, article_id: str, skip: int = 0, limit: int = 100
    ) -> list[models.Review]:
        return await self.get_multi(db=db, article_id=article_id, skip=skip, limit=limit)


review = ReviewCRUD(models.Review)
