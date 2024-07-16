from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Cookies
from sqlmodel import Session

from app import crud, models, settings
from tests.mock_objects import MOCKED_ARTICLE_1, MOCKED_ARTICLES


@pytest.fixture(name="article_1")
async def fixture_article_1(db_with_user: Session) -> models.Article:
    """
    Create an article for testing.
    """
    user = await crud.user.get(db=db_with_user, username="test_user")
    article_create = models.ArticleCreate(**MOCKED_ARTICLE_1)
    return await crud.article.create_with_owner_id(
        db=db_with_user, obj_in=article_create, owner_id=user.id
    )


@pytest.fixture(name="articles")
async def fixture_articles(db_with_user: Session) -> list[models.Article]:
    """
    Create an article for testing.
    """
    # Create 1 as a superuser
    user = await crud.user.get(db=db_with_user, username=settings.FIRST_SUPERUSER_USERNAME)
    articles = []
    article_create = models.ArticleCreate(**MOCKED_ARTICLES[0])
    articles.append(
        await crud.article.create_with_owner_id(
            db=db_with_user, obj_in=article_create, owner_id=user.id
        )
    )

    # Create 2 as a normal user
    user = await crud.user.get(db=db_with_user, username="test_user")
    for mocked_article in [MOCKED_ARTICLES[1], MOCKED_ARTICLES[2]]:
        article_create = models.ArticleCreate(**mocked_article)
        articles.append(
            await crud.article.create_with_owner_id(
                db=db_with_user, obj_in=article_create, owner_id=user.id
            )
        )
    return articles


def test_create_article_page(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that the create article page is returned.
    """
    client.cookies = normal_user_cookies
    response = client.get("/articles/create")
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/create.html"  # type: ignore


def test_handle_create_article(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can create a new article.
    """
    client.cookies = normal_user_cookies
    response = client.post(
        "/articles/create",
        data=MOCKED_ARTICLE_1,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/list.html"  # type: ignore


@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
def test_create_duplicate_article(
    db_with_user: Session,  # pylint: disable=unused-argument
    article_1: models.Article,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:  # pytest:
    """
    Test a duplicate article cannot be created.
    """
    # Try to create a duplicate article
    with pytest.raises(Exception):
        response = client.post(
            "/articles/create",
            data=MOCKED_ARTICLE_1,
        )
    # assert response.status_code == status.HTTP_200_OK
    # assert response.template.name == "article/create.html"  # type: ignore
    # assert response.context["alerts"].danger[0] == "Article already exists"  # type: ignore


def test_read_article(
    db_with_user: Session,  # pylint: disable=unused-argument
    article_1: models.Article,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can read an article.
    """
    # Read the article
    response = client.get(
        f"/article/{article_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/view.html"  # type: ignore


def test_get_article_not_found(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a article not found error is returned.
    """
    client.cookies = normal_user_cookies

    # Read the article
    response = client.get("/article/8675309")
    assert response.status_code == status.HTTP_200_OK
    assert response.url.path == "/articles"


def test_get_article_forbidden(
    db_with_user: Session,  # pylint: disable=unused-argument
    article_1: models.Article,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a forbidden error is returned when a user tries to read an article
    """
    client.cookies = normal_user_cookies

    # Read the article
    response = client.get(
        f"/article/{article_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/view.html"  # type: ignore

    # Logout
    response = client.get(
        "/logout",
    )
    assert response.status_code == status.HTTP_200_OK

    # Attempt Read the article
    response = client.get(
        f"/article/{article_1.id}",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.url.path == "/login"  # type: ignore


def test_normal_user_get_all_articles(
    db_with_user: Session,  # pylint: disable=unused-argument
    articles: list[models.Article],  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
    superuser_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a normal user can get all their own articles.
    """

    # List all articles as normal user
    client.cookies = normal_user_cookies
    response = client.get(
        "/articles",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/list.html"  # type: ignore

    # Assert only 2 articles are returned (not the superuser's article)
    assert len(response.context["articles"]) == 2  # type: ignore


def test_edit_article_page(
    db_with_user: Session,  # pylint: disable=unused-argument
    article_1: models.Article,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that the edit article page is returned.
    """
    client.cookies = normal_user_cookies
    response = client.get(
        f"/article/{article_1.id}/edit",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/edit.html"  # type: ignore

    # Test invalid article id
    response = client.get(
        f"/article/invalid_user_id/edit",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_302_FOUND
    assert response.context["alerts"].danger[0] == "Article not found"  # type: ignore
    assert response.url.path == "/articles"


def test_update_article(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    article_1: models.Article,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can update an article.
    """
    client.cookies = normal_user_cookies

    # Update the article
    response = client.post(
        f"/article/{article_1.id}/edit",  # type: ignore
        data=MOCKED_ARTICLES[1],
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/edit.html"  # type: ignore

    # View the article
    response = client.get(
        f"/article/{article_1.id}",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/view.html"  # type: ignore
    assert response.context["article"].title == MOCKED_ARTICLES[1]["title"]  # type: ignore
    assert response.context["article"].description == MOCKED_ARTICLES[1]["description"]  # type: ignore
    assert response.context["article"].url == MOCKED_ARTICLES[1]["url"]  # type: ignore

    # Test invalid article id
    response = client.post(
        f"/article/invalid_user_id/edit",  # type: ignore
        data=MOCKED_ARTICLES[1],
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.context["alerts"].danger[0] == "Article not found"  # type: ignore
    assert response.url.path == "/articles"


def test_delete_article(
    db_with_user: Session,  # pylint: disable=unused-argument
    article_1: models.Article,
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can delete an article.
    """
    client.cookies = normal_user_cookies

    # Delete the article
    response = client.get(
        f"/article/{article_1.id}/delete",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.url.path == "/articles"

    # View the article
    response = client.get(
        f"/article/{article_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.context["alerts"].danger == ["Article not found"]  # type: ignore

    # Test invalid article id
    response = client.get(
        f"/article/invalid_user_id/delete",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.context["alerts"].danger[0] == "Article not found"  # type: ignore
    assert response.url.path == "/articles"

    # Test DeleteError
    with patch("app.crud.article.remove", side_effect=crud.DeleteError):
        response = client.get(
            f"/article/123/delete",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
        assert response.context["alerts"].danger[0] == "Error deleting article"  # type: ignore


def test_list_all_articles(
    db_with_user: Session,  # pylint: disable=unused-argument
    articles: list[models.Article],  # pylint: disable=unused-argument
    client: TestClient,
    superuser_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a superuser can get all articles.
    """

    # List all articles as superuser
    client.cookies = superuser_cookies
    response = client.get(
        "/articles/all",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "article/list.html"  # type: ignore

    # Assert all 3 articles are returned
    assert len(response.context["articles"]) == 3  # type: ignore
