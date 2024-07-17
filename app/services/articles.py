from .worldanvil import import_articles
from app import settings


def import_articles_from_worldanvil():
    export_url = "https://www.worldanvil.com/world/ancient-sol-tv76/export"
    username = settings.WORLDANVIL_USERNAME
    password = settings.WORLDANVIL_PASSWORD

    imported_articles = import_articles(username=username, password=password, export_url=export_url)
    # Process the imported articles
    for article in imported_articles:
        print(f"Title: {article['title']}")
        print(f"Content: {article['content'][:100]}...")  # Print first 100 characters of content
        print(
            f"Tags: {article['tags']}"
        )  # Print first 100 characters of content# Print first 100 characters of content
        print("---")
