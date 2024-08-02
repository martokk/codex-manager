from app.views.deps import get_db
from app import crud, models, logger
from sqlmodel import Session
from typing import Dict, Optional, Any
from app.services.worldanvil import get_articles_from_worldanvil
from app.services.summarizer import generate_brief, generate_summary, generate_date_range


async def import_articles_from_worldanvil():
    """Orchestrate the import process"""
    imported_articles = get_articles_from_worldanvil()
    db = next(get_db())

    for article in imported_articles:
        await process_imported_article(db, article)

    logger.success(f"World Anvil import complete")


async def process_imported_article(db: Session, article: Dict[str, Any]) -> None:
    """Process a single article"""
    existing_article = await get_existing_article(db, article["id"])

    if not existing_article:
        await create_new_article(db, article)
    else:
        await update_existing_article(db, existing_article, article)


async def get_existing_article(db: Session, article_id: str) -> Optional[models.Article]:
    """Retrieve an existing article from the database"""
    try:
        return await crud.article.get(db=db, id=article_id)
    except crud.RecordNotFoundError:
        return None


async def create_new_article(db: Session, article: Dict[str, Any]) -> None:
    """Create a new article in the database"""
    summary = generate_summary(article["content"])
    brief = generate_brief(article["content"])
    year_start, year_end = generate_date_range(article["content"])

    new_article = models.ArticleCreate(
        id=article["id"],
        title=article["title"],
        text=article["content"],
        tags=article["tags"],
        template=article.get("template"),
        category=article.get("category"),
        summary=summary,
        brief=brief,
        year_start=year_start,
        year_end=year_end,
    )
    await crud.article.create(db=db, obj_in=new_article)
    logger.success(f"Added new article: {article['title']}")


async def update_existing_article(
    db: Session, existing_article: models.Article, new_article: Dict[str, Any]
) -> models.Article:
    """Update an existing article and create a review if necessary"""
    if has_article_changed(existing_article, new_article):
        if needs_review(existing_article, new_article):
            await create_review(db, existing_article, new_article)
            logger.info(f"Article sent for review: {existing_article.title}")
            return existing_article

        article_update = models.ArticleUpdate(
            text=new_article.get("content"),
            tags=new_article.get("tags", []),
            year_start=new_article.get("year_start"),
            year_end=new_article.get("year_end"),
            template=new_article.get("template"),
            category=new_article.get("category"),
        )
        updated_article = await crud.article.update(
            db=db, db_obj=existing_article, obj_in=article_update
        )
        logger.success(f"Article sent for review: {existing_article.title}")
        return updated_article
    else:
        logger.info(f"No changes for: {existing_article.title}")
        return existing_article


def has_article_changed(existing_article: models.Article, new_article: Dict[str, Any]) -> bool:
    """Check if the article has changed"""
    return (
        existing_article.text != new_article.get("content")
        or existing_article.tags != new_article.get("tags", [])
        or existing_article.year_start != new_article.get("year_start")
        or existing_article.year_end != new_article.get("year_end")
        or existing_article.template != new_article.get("template")
        or existing_article.category != new_article.get("category")
    )


def needs_review(existing_article: models.Article, new_article: Dict[str, Any]) -> bool:
    """Check if the article needs a review"""
    return (
        existing_article.text != str(new_article["content"])
        or not existing_article.summary
        or not existing_article.brief
    )


async def create_review(
    db: Session, existing_article: models.Article, new_article: Dict[str, Any]
) -> None:
    """Create a review for the article"""
    new_summary = generate_summary(new_article["content"])
    new_brief = generate_brief(new_article["content"])
    new_year_start, new_year_end = generate_date_range(new_article["content"])

    review = models.ReviewCreate(
        article_id=new_article["id"],
        old_summary=existing_article.summary,
        new_summary=new_summary,
        old_brief=existing_article.brief,
        new_brief=new_brief,
        old_year_start=existing_article.year_start,
        new_year_start=new_year_start,
        old_year_end=existing_article.year_end,
        new_year_end=new_year_end,
    )
    await crud.review.create(db=db, obj_in=review)
    logger.info(f"Added review for: {new_article['title']}")


async def update_article(
    db: Session, existing_article: models.Article, new_article: Dict[str, Any]
) -> None:
    """Update the existing article in the database"""
    article_update = models.ArticleUpdate(text=new_article["content"], tags=new_article["tags"])
    await crud.article.update(db=db, db_obj=existing_article, obj_in=article_update)
    logger.success(f"Updated existing article: {new_article['title']}")


async def generate_new_article_summary(
    db: Session,
    article_id: str,
) -> models.Article:
    """Generate a summary for the article and update the article"""

    existing_article = await crud.article.get(db=db, id=article_id)

    if not existing_article.text:
        return existing_article

    new_summary = generate_summary(text=existing_article.text)

    article_update = models.ArticleUpdate(
        summary=new_summary,
    )
    updated_article = await crud.article.update(
        db=db, id=existing_article.id, obj_in=article_update
    )
    logger.success(f"Updated article summary: {updated_article.title}")
    return updated_article


async def generate_new_article_brief(
    db: Session,
    article_id: str,
) -> models.Article:
    """Generate a summary for the article and update the article"""

    existing_article = await crud.article.get(db=db, id=article_id)

    if not existing_article.text:
        return existing_article

    new_brief = generate_brief(text=existing_article.text)

    article_update = models.ArticleUpdate(
        brief=new_brief,
    )
    updated_article = await crud.article.update(
        db=db, id=existing_article.id, obj_in=article_update
    )
    logger.success(f"Updated article brief: {updated_article.title}")

    return updated_article


async def generate_new_article_date_range(
    db: Session,
    article_id: str,
) -> models.Article:
    """Generate a summary for the article and update the article"""

    existing_article = await crud.article.get(db=db, id=article_id)

    if not existing_article.text:
        return existing_article

    new_year_start, new_year_end = generate_date_range(text=existing_article.text)

    article_update = models.ArticleUpdate(year_start=new_year_start, year_end=new_year_end)
    updated_article = await crud.article.update(
        db=db, id=existing_article.id, obj_in=article_update
    )
    logger.success(f"Updated article date range: {updated_article.title}")

    return updated_article


async def generate_all_ai_text(
    db: Session,
) -> None:
    """Generate a summary for the article and update the article"""

    articles = await crud.article.get_all(db=db)

    for article in articles:
        if article.brief and article.summary and article.year_start and article.year_end:
            logger.info(
                f"Article '{article.title}' already has AI text. Continuing to next article"
            )
            continue

        if not article.brief:
            await generate_new_article_brief(db=db, article_id=article.id)

        if not article.summary:
            await generate_new_article_summary(db=db, article_id=article.id)

        if not article.year_start or not article.year_end:
            await generate_new_article_date_range(db=db, article_id=article.id)

        logger.success(f"Updated all AI text for '{article.title}' article.")
