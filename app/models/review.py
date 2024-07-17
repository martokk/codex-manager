from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel
from app.core.uuid import generate_uuid_from_url
from .common import TimestampModel

if TYPE_CHECKING:
    from .article import Article  # pragma: no cover


class ReviewBase(TimestampModel, SQLModel):
    id: str = Field(default=None, primary_key=True, nullable=False)
    article_id: str = Field(foreign_key="article.id", nullable=False)
    old_summary: Optional[str] = Field(default=None)
    new_summary: Optional[str] = Field(default=None)
    old_brief: Optional[str] = Field(default=None)
    new_brief: Optional[str] = Field(default=None)


class Review(ReviewBase, table=True):
    article: "Article" = Relationship(back_populates="reviews")


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    pass
