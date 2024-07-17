from typing import TYPE_CHECKING, Optional, List, Any
from datetime import datetime
from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel
from app.core.uuid import generate_uuid_from_url
from .common import TimestampModel

if TYPE_CHECKING:
    from .user import User  # pragma: no cover


class ArticleBase(TimestampModel, SQLModel):
    id: str = Field(default=None, primary_key=True, nullable=False)
    title: str = Field(default=None)
    owner_id: str = Field(foreign_key="user.id", nullable=False, default=None)
    year_start: Optional[int] = Field(default=None)
    year_end: Optional[int] = Field(default=None)
    tags: Optional[List[str]] = Field(default_factory=list)
    text: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    brief: Optional[str] = Field(default=None)


class Article(ArticleBase, table=True):
    owner: "User" = Relationship(back_populates="articles")
    custom_codex_articles: List["CustomCodexArticle"] = Relationship(back_populates="article")
    reviews: List["Review"] = Relationship(back_populates="article")


class ArticleCreate(ArticleBase):
    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        sanitized_url = values["url"]
        article_uuid = generate_uuid_from_url(url=sanitized_url)
        return {
            **values,
            "url": sanitized_url,
            "id": values.get("id", article_uuid),
            "updated_at": datetime.utcnow(),
        }


class ArticleUpdate(ArticleBase):
    pass


class ArticleRead(ArticleBase):
    pass
