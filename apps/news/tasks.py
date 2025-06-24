"""
Celery tasks for fetching and caching news articles
This module contains Celery tasks that fetch news articles from external APIs,
store them in the database, and cache them in Redis.
Located at: apps/news/tasks.py
"""

import requests
import logging
import redis
import json
import re
from datetime import timedelta
from dateutil import parser
from celery import shared_task
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from apps.news.models import Article, NewsSource
from apps.users.models import Category

# Define a module-level logger
logger = logging.getLogger(__name__)

# Initialize Redis client using a configurable host (default to localhost)
REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
redis_client = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
)

# Set Redis expiry time for news articles (28 days)
REDIS_ARTICLE_EXPIRY = timedelta(days=28).total_seconds()


# Helper function to generate Redis keys dynamically
def get_redis_key(source):
    return f"news:{source.lower()}"


def cache_articles(articles, source, max_articles=100):
    """
    Cache news articles in Redis using a rolling cache approach.
    - Avoids redundant storage by checking existing articles before pushing.
    - Stores only new articles while maintaining a max limit.
    - Handles Redis connection failures gracefully.
    """
    key = get_redis_key(source)
    try:
        existing_articles = redis_client.lrange(key, 0, -1)
        existing_urls = {
            json.loads(article)["url"] for article in existing_articles
        }
        new_articles = [
            json.dumps(article) for article in articles if article
            ["url"] not in existing_urls
        ]
        if not new_articles:
            logger.info(f"No new articles to cache for {source}.")
            return
        redis_client.lpush(
            key, *new_articles
        )  # Bulk insert for efficiency
        redis_client.ltrim(
            key, 0, max_articles - 1
        )  # Keep latest 100
        redis_client.expire(
            key, int(REDIS_ARTICLE_EXPIRY)
        )  # Set expiry to 28 days
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")


@shared_task
def fetch_news_articles():
    """Fetch top headlines from News API and
    store them in the database and Redis cache."""
    key = get_redis_key("newsapi")
    if redis_client.exists(key):
        logger.info("News articles already cached, skipping fetch.")
        return "News articles already cached, skipping fetch."

    api_key = settings.NEWS_API_KEY
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "gb",
        "apiKey": api_key,
        "pageSize": 20,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching articles from News API: {e}")
        return f"Error fetching articles from News API: {e}"

    data = response.json()
    articles_data = data.get("articles", [])
    created_count = 0
    cached_articles = []

    CATEGORY_KEYWORDS = {
        "Politics": [
            "election", "government", "minister", "policy", "parliament"
        ],
        "Business": [
            "market", "economy", "trade", "inflation", "stock"
        ],
        "Technology": [
            "AI", "tech", "software", "hardware", "startup"
        ],
        "Sports": [
            "match", "goal", "team", "tournament", "league"
        ],
        "World News": [
            "UN", "international", "global", "conflict", "diplomacy"
        ],
        "Entertainment": [
            "movie", "music", "celebrity", "TV", "film"
        ],
    }

    for article_data in articles_data:
        title = article_data.get("title")
        url_article = article_data.get("url")
        published_str = article_data.get("publishedAt")
        if not title or not url_article:
            logger.warning("Skipping article due to missing title or URL")
            continue

        try:
            published_at = parser.parse(
                published_str
            ) if published_str else timezone.now()
        except (TypeError, ValueError):
            published_at = timezone.now()

        source_info = article_data.get("source", {})
        source_name = source_info.get("name") or "Unknown"
        news_source = get_or_create_news_source(source_name)
        content = article_data.get("content", "")
        summary = article_data.get("description", "")
        image_url = article_data.get("urlToImage")
        category = None
        combined_text = re.sub(
            r"[^\w\s]", "", f"{title} {summary} {content}".lower()
        )

        for cat_name, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword.lower() in combined_text for keyword in keywords):
                try:
                    category = Category.objects.get(name=cat_name)
                except Category.DoesNotExist:
                    category = None
                break

        if not category:
            logger.debug(f"No category matched for: {title}")
            try:
                category = Category.objects.get(name="General")
            except Category.DoesNotExist:
                category = None
                logger.warning("Fallback category 'General' does not exist.")

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
                "imported": True,
            }
        )
        if article_created:
            created_count += 1

        cached_articles.append({
            "title": title,
            "url": url_article,
            "summary": summary,
            "image_url": image_url,
            "published_at": published_at.isoformat(),
            "source": source_name,
        })

    cache_articles(cached_articles, source="newsapi")
    message = (
        f"News articles fetched and stored successfully."
        f"{created_count} new articles created."
    )
    logger.info(message)
    return message


def get_or_create_news_source(source_name):
    """Helper function to get or create a NewsSource object."""
    news_source, _ = NewsSource.objects.get_or_create(
        name=source_name,
        defaults={
            "slug": slugify(source_name),
            "website": "",
            "description": "",
        }
    )
    return news_source
