import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import re
from app import settings, logger


def login_to_worldanvil(
    session: requests.Session, username: str, password: str
) -> requests.Session | None:
    login_url = "https://www.worldanvil.com/login_check"
    login_page = session.get("https://www.worldanvil.com/login")
    soup = BeautifulSoup(login_page.content, "lxml")

    csrf_token_input = soup.find("input", {"type": "hidden", "name": "_csrf_token"})
    csrf_token = csrf_token_input.get("value")

    login_data = {
        "_csrf_token": csrf_token,
        "_username": username,
        "_password": password,
        "_remember_me": "on",
        "_submit": "Log in",
    }

    response = session.post(login_url, data=login_data)
    return session if response.ok else None


def get_export_content(session: requests.Session, export_url: str) -> Optional[str]:
    response = session.get(export_url)
    if response.ok:
        return str(response.text)
    else:
        return None


def extract_article_id(soup: BeautifulSoup) -> str:
    article_div = soup.find("div", class_="article-print-container")
    if not article_div or "id" not in article_div.attrs:
        raise
    return str(article_div["id"]).replace("article-", "")


def clean_title(title: str) -> str:
    """Clean the title by removing underscores and parenthetical content."""
    title = re.sub(r"^__", "", title)
    title = re.sub(r"\s*\([^)]*\)\s*$", "", title)
    return title.replace("_", "").strip()


def extract_title(soup: BeautifulSoup) -> str:
    """Extract the title from the article HTML."""
    title_elem = soup.find("h1", class_="m-b-0")
    return clean_title(title_elem.text.strip()) if title_elem else "Untitled"


def extract_content(soup: BeautifulSoup) -> str:
    """Extract the main content from the article HTML."""
    content_div = soup.find("div", class_="article-content-left")
    return str(content_div.get_text(separator="\n", strip=True)) if content_div else ""


def extract_tags(soup: BeautifulSoup) -> list[str]:
    """Extract tags from the article HTML."""
    tags: list[str] = []

    # Look for the metadata div
    metadata_div = soup.find("div", id="metadata")
    if not metadata_div:
        return tags

    # Look for the specific div containing tags
    tags_div = metadata_div.find("div", class_="col-md-3")
    if tags_div:
        tags_row = tags_div.find("div", class_="row")
        if tags_row:
            tags_value_div = tags_row.find("div", class_="metadata-value")
            if tags_value_div:
                # Find all tag links
                tag_links = tags_value_div.find_all("a", class_="explorer-tag")
                tags = [tag.text.strip() for tag in tag_links]

    return tags


def extract_template(soup: BeautifulSoup) -> Optional[str]:
    """Extract the article template from the article HTML."""
    metadata_div = soup.find("div", id="metadata")
    if metadata_div:
        template_row = metadata_div.find(
            "div",
            lambda tag: tag.name == "div" and tag.find("div", string="Article template"),
            class_="row",
        )
        if template_row:
            template_value = template_row.find("div", class_="metadata-value")
            if template_value:
                return template_value.text.strip()
    return None


def extract_category(soup: BeautifulSoup) -> Optional[str]:
    """Extract the category from the article HTML."""
    metadata_div = soup.find("div", id="metadata")
    if not metadata_div:
        return None

    category_label = metadata_div.find("div", class_="metadata-label", string="Category")
    if category_label:
        category_value = category_label.find_next("div", class_="metadata-value")
        if category_value:
            category_link = category_value.find("a")
            if category_link:
                return category_link.text.strip()

    return None


def parse_single_article(article_html: str) -> dict[str, Any]:
    """Parse a single article from its HTML content."""
    soup = BeautifulSoup(article_html, "lxml")

    id_ = extract_article_id(soup)
    title = extract_title(soup)
    content = extract_content(soup)
    tags = extract_tags(soup)
    category = extract_category(soup)
    template = extract_template(soup)

    return {
        "id": id_,
        "title": title,
        "content": content,
        "tags": tags,
        "category": category,
        "template": template,
    }


def split_articles(full_html: str) -> list[Any]:
    """Split the full HTML into individual article chunks."""
    soup = BeautifulSoup(full_html, "lxml")
    return list(soup.find_all("div", class_="article-print-container"))


def get_articles_from_html(html_content: str) -> list[Any]:
    """Import all articles from the full HTML content."""
    article_divs = split_articles(html_content)
    return [parse_single_article(str(article_div)) for article_div in article_divs]


def import_articles(username: str, password: str, export_url: str) -> List[Dict[str, Any]]:
    with requests.Session() as session:
        logged_in_session = login_to_worldanvil(session, username, password)
        if not logged_in_session:
            raise Exception("Failed to log in to WorldAnvil")

        html_content = get_export_content(logged_in_session, export_url)
        if not html_content:
            raise Exception("Failed to retrieve export content from WorldAnvil")

        articles = get_articles_from_html(html_content)

        return articles


def get_articles_from_worldanvil() -> List[Dict[str, Any]]:
    """Login to WorldAnvil and retrieve all articles"""
    export_url = "https://www.worldanvil.com/world/ancient-sol-tv76/export"
    username = settings.WORLDANVIL_USERNAME
    password = settings.WORLDANVIL_PASSWORD

    return import_articles(username=username, password=password, export_url=export_url)
