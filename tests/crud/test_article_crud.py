from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from app import crud, models
from tests.mock_objects import MOCKED_ARTICLE_1, MOCKED_ARTICLES


async def get_mocked_article(db: Session) -> models.Article:
    """
    Create a mocked article.
    """
    # Create an article with an owner
    owner = await crud.user.get(db=db, username="test_user")
    article_create = models.ArticleCreate(**MOCKED_ARTICLE_1)

    return await crud.article.create_with_owner_id(db=db, obj_in=article_create, owner_id=owner.id)


async def test_create_article(db_with_user: Session) -> None:
    """
    Test creating a new article with an owner.
    """
    created_article = await get_mocked_article(db=db_with_user)

    # Check the article was created
    assert created_article.title == MOCKED_ARTICLE_1["title"]
    assert created_article.description == MOCKED_ARTICLE_1["description"]
    assert created_article.owner_id is not None


async def test_get_article(db_with_user: Session) -> None:
    """
    Test getting an article by id.
    """
    created_article = await get_mocked_article(db=db_with_user)

    # Get the article
    db_article = await crud.article.get(db=db_with_user, id=created_article.id)
    assert db_article
    assert db_article.id == created_article.id
    assert db_article.title == created_article.title
    assert db_article.description == created_article.description
    assert db_article.owner_id == created_article.owner_id


async def test_update_article(db_with_user: Session) -> None:
    """
    Test updating an article.
    """
    created_article = await get_mocked_article(db=db_with_user)

    # Update the article
    db_article = await crud.article.get(db=db_with_user, id=created_article.id)
    db_article_update = models.ArticleUpdate(description="New Description")
    updated_article = await crud.article.update(
        db=db_with_user, id=created_article.id, obj_in=db_article_update
    )
    assert db_article.id == updated_article.id
    assert db_article.title == updated_article.title
    assert updated_article.description == "New Description"
    assert db_article.owner_id == updated_article.owner_id


async def test_update_article_without_filter(db_with_user: Session) -> None:
    """
    Test updating an article without a filter.
    """
    created_article = await get_mocked_article(db=db_with_user)

    # Update the article (without a filter)
    await crud.article.get(db=db_with_user, id=created_article.id)
    db_article_update = models.ArticleUpdate(description="New Description")
    with pytest.raises(ValueError):
        await crud.article.update(db=db_with_user, obj_in=db_article_update)


async def test_delete_article(db_with_user: Session) -> None:
    """
    Test deleting an article.
    """
    created_article = await get_mocked_article(db=db_with_user)

    # Delete the article
    await crud.article.remove(db=db_with_user, id=created_article.id)
    with pytest.raises(crud.RecordNotFoundError):
        await crud.article.get(db=db_with_user, id=created_article.id)


async def test_delete_article_delete_error(db_with_user: Session, mocker: MagicMock) -> None:
    """
    Test deleting an article with a delete error.
    """
    mocker.patch("app.crud.article.get", return_value=None)
    with pytest.raises(crud.DeleteError):
        await crud.article.remove(db=db_with_user, id="00000001")


async def test_get_all_articles(db_with_user: Session) -> None:
    """
    Test getting all articles.
    """
    # Create some articles
    for i, article in enumerate(MOCKED_ARTICLES):
        article_create = models.ArticleCreate(**article)
        await crud.article.create_with_owner_id(
            db=db_with_user, obj_in=article_create, owner_id=f"0000000{i}"
        )

    # Get all articles
    articles = await crud.article.get_all(db=db_with_user)
    assert len(articles) == len(MOCKED_ARTICLES)
