from typing import TYPE_CHECKING, Optional, List, Any
from datetime import datetime
from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel, JSON, Column
from .common import TimestampModel

if TYPE_CHECKING:
    from .review import Review  # pragma: no cover
    from .custom_codex_article import CustomCodexArticle  # pragma: no cover


class ArticleBase(TimestampModel, SQLModel):
    id: str = Field(default=None, primary_key=True, nullable=False)
    title: str = Field(default=None)
    year_start: Optional[int] = Field(default=None)
    year_end: Optional[int] = Field(default=None)
    tags: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    text: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    brief: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    template: Optional[str] = Field(default=None)


class Article(ArticleBase, table=True):
    custom_codex_articles: List["CustomCodexArticle"] = Relationship(back_populates="article")
    reviews: List["Review"] = Relationship(back_populates="article")


class ArticleCreate(ArticleBase):
    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        return {
            **values,
            "updated_at": datetime.utcnow(),
        }


class ArticleUpdate(SQLModel):
    title: Optional[str] = None
    text: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = Field(default=None)
    brief: Optional[str] = Field(default=None)
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    category: Optional[str] = None
    template: Optional[str] = None


class ArticleRead(ArticleBase):
    pass
