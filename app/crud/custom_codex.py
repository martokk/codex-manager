from sqlmodel import Session

from app import models

from .base import BaseCRUD


class CustomCodexCRUD(
    BaseCRUD[models.CustomCodex, models.CustomCodexCreate, models.CustomCodexUpdate]
):
    pass


custom_codex = CustomCodexCRUD(models.CustomCodex)
