from typing import TYPE_CHECKING, Any, Optional, List
from datetime import datetime
from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel
from app.core.uuid import generate_uuid_from_url, generate_uuid_random
from .common import TimestampModel

if TYPE_CHECKING:
    from .custom_codex import CustomCodex  # pragma: no cover
    from .article import Article  # pragma: no cover


class CustomCodexArticleBase(TimestampModel, SQLModel):
    id: str = Field(default=None, primary_key=True, nullable=False)
    codex_id: str = Field(foreign_key="customcodex.id", nullable=False)
    article_id: str = Field(foreign_key="article.id", nullable=False)
    article_type: str = Field(default=None)  # None, Full, Brief, Custom
    custom_text: Optional[str] = Field(default=None)


class CustomCodexArticle(CustomCodexArticleBase, table=True):
    custom_codex: "CustomCodex" = Relationship(back_populates="custom_codex_articles")
    article: "Article" = Relationship(back_populates="custom_codex_articles")


class CustomCodexArticleCreate(CustomCodexArticleBase):

    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["id"] = values.get("id", generate_uuid_random())
        return values


class CustomCodexArticleUpdate(CustomCodexArticleBase):
    pass


class CustomCodexArticleRead(CustomCodexArticleBase):
    pass
