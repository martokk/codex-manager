from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel
from app.core.uuid import generate_uuid_from_url, generate_uuid_random
from .common import TimestampModel
from typing import Any

if TYPE_CHECKING:
    from .custom_codex_article import CustomCodexArticle  # pragma: no cover


class CustomCodexBase(TimestampModel, SQLModel):
    id: str = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(default=None)
    context_length: Optional[int] = Field(default=None)
    year_start: Optional[int] = Field(default=None)
    year_end: Optional[int] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)


class CustomCodex(CustomCodexBase, table=True):
    custom_codex_articles: List["CustomCodexArticle"] = Relationship(back_populates="custom_codex")


class CustomCodexCreate(CustomCodexBase):

    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["id"] = values.get("id", generate_uuid_random())
        return values


class CustomCodexUpdate(CustomCodexBase):
    pass


class CustomCodexRead(CustomCodexBase):
    pass
