import requests
from dateutil import parser
from celery import shared_task
from django.conf import settings
from django.utils.text import slugify
from apps.news.models import Article, NewsSource
from apps.users.models import Category


@shared_task
def fetch_news_articles():
    """
    Fetch top headlines from News API and store them in the database.
    """
    api_key = settings.NEWS_API_KEY
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "apiKey": api_key,
        "pageSize": 20,  # Fetch 20 articles per call
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        # Log error
        print(f"Error fetching articles: {e}")
        return

    data = response.json()
    articles_data = data.get("articles", [])

    for article_data in articles_data:
        title = article_data.get("title")
        content = article_data.get("content") or ""
        summary = article_data.get("description") or ""
        image_url = article_data.get("urlToImage")
        published_str = article_data.get("publishedAt")
        url_article = article_data.get("url")
        source_info = article_data.get("source", {})
        source_name = source_info.get("name") or "Unknown"

        # Parse the published date string into a datetime object.
        try:
            published_at = parser.parse(published_str)
        except (TypeError, ValueError):
            published_at = None

        # Get or create the NewsSource record
        news_source, created = NewsSource.objects.get_or_create(
            name=source_name,
            defaults={
                "slug": slugify(source_name),
                "website": "",  # Optionally, parse the website if available.
                "description": "",
            }
        )

        # Determine a category based on mapping, else leave it as None.
        category = None

        # Create the article if it does not exist yet.
        # Using url as a unique field to prevent duplicates.
        Article.objects.get_or_create(
            url=url_article,
            defaults={
                "title": title,
                "content": content,
                "summary": summary,
                "image_url": image_url,
                "published_at": published_at,
                "source": news_source,
                "category": category,
            }
        )

    print("News articles fetched and stored successfully.")
