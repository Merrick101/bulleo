import requests
import logging
from dateutil import parser
from celery import shared_task
from django.conf import settings
from django.utils.text import slugify
from apps.news.models import Article, NewsSource
from apps.users.models import Category

# Define a module-level logger
logger = logging.getLogger(__name__)


@shared_task
def fetch_news_articles():
    """
    Fetch top headlines from News API and store them in the database.
    Uses the News API 'top-headlines' endpoint.
    """
    api_key = settings.NEWS_API_KEY
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "gb",
        "apiKey": api_key,
        "pageSize": 20,  # Fetch 20 articles per call
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        error_message = f"Error fetching articles from News API: {e}"
        logger.error(error_message)
        return error_message

    data = response.json()
    articles_data = data.get("articles", [])

    created_count = 0

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
        news_source, _ = NewsSource.objects.get_or_create(
            name=source_name,
            defaults={
                "slug": slugify(source_name),
                "website": "",  # Optionally update if available
                "description": "",
            }
        )

        # Determine a category based on mapping; for now, leave as None.
        category = None

        # Create the article if it does not exist yet.
        # Using the article URL as a unique field to prevent duplicates.
        _, article_created = Article.objects.get_or_create(
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
        if article_created:
            created_count += 1

    message = f"News articles fetched and stored successfully. {created_count} new articles created."
    logger.info(message)
    return message


@shared_task
def fetch_guardian_articles():
    """
    Fetch articles from the Guardian API using the 'search' endpoint for specific sections
    (mapped from the onboarding categories) and store them in the database.
    """
    api_key = settings.GUARDIAN_API_KEY
    # Map onboarding categories to Guardian sections
    sections = {
        "World News": "world",
        "Politics": "politics",
        "Business": "business",
        "Technology": "technology",
        "Sports": "sport",
        "Entertainment": "culture",  # You can adjust this mapping as needed.
    }

    total_created = 0
    base_url = "https://content.guardianapis.com/search"
    # Common query parameters (requesting additional fields for summary and image)
    common_params = {
        "api-key": api_key,
        "page-size": 20,
        "show-fields": "trailText,thumbnail"
    }

    for category_name, section in sections.items():
        # Update parameters for the specific section
        params = common_params.copy()
        params["section"] = section

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error fetching Guardian articles for {section}: {e}")
            continue

        data = response.json()
        results = data.get("response", {}).get("results", [])
        created_count = 0

        for item in results:
            title = item.get("webTitle")
            url_article = item.get("webUrl")
            published_str = item.get("webPublicationDate")
            fields = item.get("fields", {})
            summary = fields.get("trailText", "")
            image_url = fields.get("thumbnail", "")

            try:
                published_at = parser.parse(published_str)
            except (TypeError, ValueError):
                published_at = None

            source_name = "The Guardian"
            news_source, _ = NewsSource.objects.get_or_create(
                name=source_name,
                defaults={
                    "slug": slugify(source_name),
                    "website": "https://www.theguardian.com",
                    "description": f"The Guardian {section.capitalize()} Articles",
                }
            )

            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                category = None

            # Create the article if it does not exist yet (using URL as unique identifier)
            _, article_created = Article.objects.get_or_create(
                url=url_article,
                defaults={
                    "title": title,
                    "content": "",  # Guardian API might not provide full content; adjust if you fetch more fields.
                    "summary": summary,
                    "image_url": image_url,
                    "published_at": published_at,
                    "source": news_source,
                    "category": category,
                }
            )
            if article_created:
                created_count += 1

        logger.info(f"Guardian {section} fetch complete. {created_count} new articles created for {category_name}.")
        total_created += created_count

    message = f"Guardian fetch complete. Total new articles created: {total_created}."
    logger.info(message)
    return message
