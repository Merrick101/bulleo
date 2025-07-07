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
from apps.news.models import Article, NewsSource, Category

# Define a module-level logger
logger = logging.getLogger(__name__)

# Initialize Redis client using full REDIS_URL (e.g., from Upstash)
REDIS_URL = getattr(settings, 'REDIS_URL')
redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

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
def delete_expired_articles():
    """
    Delete articles older than 28 days from the database.
    This does not affect articles manually created or pinned.
    """
    threshold_date = timezone.now() - timedelta(days=28)
    old_articles = Article.objects.filter(
        imported=True, published_at__lt=threshold_date
    )
    count = old_articles.count()
    old_articles.delete()
    logger.info(f"Deleted {count} expired articles older than 28 days.")
    return f"{count} expired articles deleted."


def get_category_from_topic(topic):
    """
    Map GNews topic to a Category instance.
    """
    topic_map = {
        "world": "World News",
        "nation": "Politics",
        "business": "Business",
        "technology": "Technology",
        "sports": "Sports",
        "entertainment": "Entertainment",
    }
    cat_name = topic_map.get(topic.lower()) if topic else None
    if cat_name:
        try:
            return Category.objects.get(name=cat_name)
        except Category.DoesNotExist:
            logger.warning(f"Category '{cat_name}' from topic not found.")
    return None


def get_category_from_keywords(title, summary, content):
    """
    Match article content against keyword map to determine category.
    """
    combined_text = re.sub(
        r"[^\w\s]", "", f"{title} {summary} {content}".lower()
    )
    keyword_map = {
        "Politics":
            ["election", "government", "minister", "policy", "parliament"],
        "Business":
            ["market", "economy", "trade", "inflation", "stock"],
        "Technology":
            ["AI", "tech", "software", "hardware", "startup"],
        "Sports":
            ["match", "goal", "team", "tournament", "league"],
        "World News":
            ["UN", "international", "global", "conflict", "diplomacy"],
        "Entertainment":
            ["movie", "music", "celebrity", "TV", "film"],
    }
    for cat_name, keywords in keyword_map.items():
        if any(keyword.lower() in combined_text for keyword in keywords):
            try:
                return Category.objects.get(name=cat_name)
            except Category.DoesNotExist:
                logger.warning(
                    f"Keyword-matched category '{cat_name}' not found."
                )
                return None
    return None


@shared_task
def fetch_news_articles():
    """
    Fetch top headlines from GNews API, categorize, store, and cache.
    """

    if getattr(settings, "SKIP_FETCH_IF_CACHED", True):
        key = get_redis_key("gnews")
        if redis_client.exists(key):
            logger.info("News articles already cached, skipping fetch.")
            return "News articles already cached, skipping fetch."

    api_key = settings.GNEWS_API_KEY
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        "country": "gb",
        "token": api_key,
        "pageSize": 20,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching articles from GNews API: {e}")
        return f"Error fetching articles from GNews API: {e}"

    data = response.json()
    articles_data = data.get("articles", [])
    created_count = 0
    cached_articles = []

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
        image_url = article_data.get("image")
        topic = article_data.get("topic", "")  # GNews may include this

        # Hybrid matching logic
        category = get_category_from_topic(topic)
        if not category:
            category = get_category_from_keywords(title, summary, content)

        if not category:
            try:
                category = Category.objects.get(name="General")
            except Category.DoesNotExist:
                logger.warning("Fallback category 'General' does not exist.")
                category = None

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

    cache_articles(cached_articles, source="gnews")
    message = (
        f"GNews articles fetched and stored successfully. "
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


@shared_task
def redis_heartbeat():
    """
    Simple task to ping Redis to prevent free-tier expiry on Upstash.
    """
    try:
        redis_client.ping()
    except redis.RedisError as e:
        logger.warning(f"Heartbeat ping to Redis failed: {e}")
