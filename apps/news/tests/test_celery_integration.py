"""
Integration tests for Celery tasks in the News app.
Located at: apps/news/tests/test_celery_integration.py
"""

import pytest
from unittest import mock
from datetime import timedelta
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from apps.news.tasks import (
    fetch_news_articles,
    delete_expired_articles,
    redis_heartbeat,
)
from apps.news.models import Article


@pytest.mark.django_db
def test_delete_expired_articles_task():
    # Create dummy expired article
    Article.objects.create(
        title="Old Article",
        content="Old content",
        url="https://example.com/old-article",
        published_at=timezone.now() - timedelta(days=30),
        imported=True
    )
    assert Article.objects.count() == 1

    # Run cleanup task
    result = delete_expired_articles()
    assert "1 expired articles deleted." in result
    assert Article.objects.count() == 0


@pytest.mark.django_db
@mock.patch("apps.news.tasks.redis_client")
@mock.patch("apps.news.tasks.requests.get")
def test_fetch_news_articles_task(mock_get, mock_redis):
    # Setup mock API response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "articles": [
            {
                "title": "Test News",
                "url": "https://example.com/test-news",
                "publishedAt": timezone.now().isoformat(),
                "content": "Content here",
                "description": "Desc",
                "urlToImage": "https://example.com/image.jpg",
                "source": {"name": "BBC"},
            }
        ]
    }
    mock_redis.exists.return_value = False  # allow fetch

    result = fetch_news_articles()
    assert "News articles fetched and stored successfully." in result
    assert Article.objects.filter(title="Test News").exists()


@pytest.mark.django_db
def test_create_dummy_schedule_objects():
    # Create interval schedule (every 10 minutes)
    interval = IntervalSchedule.objects.create(
        every=10, period=IntervalSchedule.MINUTES
    )

    # Link to a periodic task
    task = PeriodicTask.objects.create(
        interval=interval,
        name="Test Fetch News Task",
        task="apps.news.tasks.fetch_news_articles",
        description="Dummy task for testing Celery Beat integration"
    )

    assert task.interval.every == 10
    assert "fetch_news_articles" in task.task


@mock.patch("apps.news.tasks.redis_client")
def test_redis_heartbeat(mock_redis):
    redis_heartbeat()
    mock_redis.ping.assert_called_once()
