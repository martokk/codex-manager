from typing import TYPE_CHECKING, Optional, List, Any
from datetime import datetime
from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel
from app.core.uuid import generate_uuid_random
from .common import TimestampModel

if TYPE_CHECKING:
    from .article import Article  # pragma: no cover


class ReviewBase(TimestampModel, SQLModel):
    id: str = Field(
        primary_key=True,
        index=True,
        nullable=False,
        default=None,
    )
    article_id: str = Field(foreign_key="article.id", nullable=False)
    old_summary: Optional[str] = Field(default=None)
    new_summary: Optional[str] = Field(default=None)
    old_brief: Optional[str] = Field(default=None)
    new_brief: Optional[str] = Field(default=None)


class Review(ReviewBase, table=True):
    article: "Article" = Relationship(back_populates="reviews")


class ReviewCreate(ReviewBase):

    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["id"] = values.get("id", generate_uuid_random())
        return values


class ReviewUpdate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    pass
