from fastapi.testclient import TestClient
from sqlmodel import Session

from app import settings
from tests.mock_objects import MOCKED_ARTICLE_1, MOCKED_ARTICLES


def test_create_article(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can create a new article.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=superuser_token_headers,
        json=MOCKED_ARTICLE_1,
    )
    assert response.status_code == 201
    article = response.json()
    assert article["title"] == MOCKED_ARTICLE_1["title"]
    assert article["description"] == MOCKED_ARTICLE_1["description"]
    assert article["url"] == MOCKED_ARTICLE_1["url"]
    assert article["owner_id"] is not None
    assert article["id"] is not None


def test_create_duplicate_article(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test a duplicate article cannot be created.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=superuser_token_headers,
        json=MOCKED_ARTICLE_1,
    )
    assert response.status_code == 201

    # Try to create a duplicate article
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=superuser_token_headers,
        json=MOCKED_ARTICLE_1,
    )
    assert response.status_code == 200
    duplicate = response.json()
    assert duplicate["detail"] == "Article already exists"


def test_read_article(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can read an article.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=superuser_token_headers,
        json=MOCKED_ARTICLE_1,
    )
    assert response.status_code == 201
    created_article = response.json()

    # Read Article
    response = client.get(
        f"{settings.API_V1_PREFIX}/article/{created_article['id']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    read_article = response.json()

    assert read_article["title"] == MOCKED_ARTICLE_1["title"]
    assert read_article["description"] == MOCKED_ARTICLE_1["description"]
    assert read_article["url"] == MOCKED_ARTICLE_1["url"]
    assert read_article["owner_id"] is not None
    assert read_article["id"] is not None


def test_get_article_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a article not found error is returned.
    """
    response = client.get(
        f"{settings.API_V1_PREFIX}/article/1",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Article not found"


def test_get_article_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.get(
        f"{settings.API_V1_PREFIX}/article/5kwf8hFn",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_superuser_get_all_articles(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    """
    Test that a superuser can get all articles.
    """

    # Create 3 articles
    for article in MOCKED_ARTICLES:
        response = client.post(
            f"{settings.API_V1_PREFIX}/article/",
            headers=superuser_token_headers,
            json=article,
        )
        assert response.status_code == 201

    # Get all articles as superuser
    response = client.get(
        f"{settings.API_V1_PREFIX}/article/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    articles = response.json()
    assert len(articles) == 3


def test_normal_user_get_all_articles(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
) -> None:
    """
    Test that a normal user can get all their own articles.
    """
    # Create 2 articles as normal user
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=normal_user_token_headers,
        json=MOCKED_ARTICLES[0],
    )
    assert response.status_code == 201
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=normal_user_token_headers,
        json=MOCKED_ARTICLES[1],
    )
    assert response.status_code == 201

    # Create 1 article as super user
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=superuser_token_headers,
        json=MOCKED_ARTICLES[2],
    )
    assert response.status_code == 201

    # Get all articles as normal user
    response = client.get(
        f"{settings.API_V1_PREFIX}/article/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    articles = response.json()
    assert len(articles) == 2


def test_update_article(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can update an article.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=superuser_token_headers,
        json=MOCKED_ARTICLE_1,
    )
    assert response.status_code == 201
    created_article = response.json()

    # Update Article
    update_data = MOCKED_ARTICLE_1.copy()
    update_data["title"] = "Updated Title"
    response = client.patch(
        f"{settings.API_V1_PREFIX}/article/{created_article['id']}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_article = response.json()
    assert updated_article["title"] == update_data["title"]

    # Update wrong article
    response = client.patch(
        f"{settings.API_V1_PREFIX}/article/99999",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 404


def test_update_article_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.patch(
        f"{settings.API_V1_PREFIX}/article/5kwf8hFn",
        headers=normal_user_token_headers,
        json=MOCKED_ARTICLE_1,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_article(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can delete an article.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/article/",
        headers=superuser_token_headers,
        json=MOCKED_ARTICLE_1,
    )
    assert response.status_code == 201
    created_article = response.json()

    # Delete Article
    response = client.delete(
        f"{settings.API_V1_PREFIX}/article/{created_article['id']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204

    # Delete wrong article
    response = client.delete(
        f"{settings.API_V1_PREFIX}/article/99999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_delete_article_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.delete(
        f"{settings.API_V1_PREFIX}/article/5kwf8hFn",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
