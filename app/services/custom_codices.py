from typing import List, Optional
from sqlmodel import Session
from app import models, crud
from app.services.tokenizer import count_tokens


# async def get_all_articles(db: Session) -> List[models.Article]:
#     """
#     Retrieve all articles from the database.
#     """
#     return await crud.article.get_all(db)


# async def get_custom_codex(db: Session, codex_id: str) -> Optional[models.CustomCodex]:
#     """
#     Retrieve a custom codex by its ID.
#     """
#     return await crud.custom_codex.get(db, id=codex_id)


# async def get_custom_codex_articles(db: Session, codex_id: str) -> List[models.CustomCodexArticle]:
#     """
#     Retrieve all custom codex articles for a given codex ID.
#     """
#     return await crud.custom_codex_article.get_multi_by_codex_id(db, codex_id=codex_id)


async def update_custom_codex_article(
    db: Session,
    codex_id: str,
    article_id: str,
    article_type: str,
    custom_text: Optional[str] = None,
) -> models.CustomCodexArticle:
    """
    Update or create a custom codex article.
    """
    existing_article = await crud.custom_codex_article.get(
        db=db, codex_id=codex_id, article_id=article_id
    )
    if existing_article:
        update_data = models.CustomCodexArticleUpdate(
            article_type=article_type,
            custom_text=custom_text,
            codex_id=codex_id,
            article_id=article_id,
        )
        return await crud.custom_codex_article.update(
            db, db_obj=existing_article, obj_in=update_data
        )
    else:
        create_data = models.CustomCodexArticleCreate(
            codex_id=codex_id,
            article_id=article_id,
            article_type=article_type,
            custom_text=custom_text,
        )
        return await crud.custom_codex_article.create(db, obj_in=create_data)


async def calculate_context_length(db: Session, codex_id: str) -> int:
    """
    Calculate the total context length for a custom codex.
    """
    custom_codex_articles = await crud.custom_codex_article.get_multi_by_codex_id(
        db, codex_id=codex_id
    )
    total_tokens = 0
    for cca in custom_codex_articles:
        article = await crud.article.get(db=db, id=cca.article_id)
        if cca.article_type == "Full":
            total_tokens += count_tokens(article.text)
        elif cca.article_type == "Summary":
            total_tokens += count_tokens(article.summary)
        elif cca.article_type == "Brief":
            total_tokens += count_tokens(article.brief)
        elif cca.article_type == "Custom":
            total_tokens += count_tokens(cca.custom_text)
    return total_tokens


async def update_article_types_by_criteria(
    db: Session,
    codex_id: str,
    year_start: Optional[int],
    year_end: Optional[int],
    tags: Optional[List[str]],
) -> None:
    """
    Update article types to "Full" based on year range and tags criteria.
    """
    articles = await crud.article.get_all(db)
    for article in articles:
        if (
            (year_start is None or article.year_start >= year_start)
            and (year_end is None or article.year_end <= year_end)
            and (not tags or any(tag in article.tags for tag in tags))
        ):
            await update_custom_codex_article(db, codex_id, article.id, "Full")


async def batch_update_custom_codex_articles(
    db: Session, codex_id: str, article_types: dict
) -> None:
    """
    Batch update custom codex articles.
    """
    for article_id, article_type in article_types.items():
        await crud.custom_codex_article.update(
            db=db, codex_id=codex_id, article_id=article_id, article_type=article_type
        )
