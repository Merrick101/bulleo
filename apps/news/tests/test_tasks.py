import pytest
import json
from unittest import mock
from datetime import timedelta
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from apps.news.models import Article, NewsSource
from apps.news.tasks import (
    fetch_news_articles,
    delete_expired_articles,
    redis_heartbeat,
    cache_articles,
)


@pytest.mark.django_db
def test_delete_expired_articles_creates_and_deletes():
    source = NewsSource.objects.create(name="Test Source", slug="test-source")
    old_article = Article.objects.create(
        title="Old News",
        url="https://example.com/old",
        content="Old content",
        published_at=timezone.now() - timedelta(days=30),
        source=source,
        imported=True,
    )

    fresh_article = Article.objects.create(
        title="Recent News",
        url="https://example.com/recent",
        content="Recent content",
        published_at=timezone.now(),
        source=source,
        imported=True,
    )

    deleted_count_msg = delete_expired_articles()
    assert Article.objects.filter(pk=old_article.pk).count() == 0
    assert Article.objects.filter(pk=fresh_article.pk).exists()
    assert "expired articles deleted" in deleted_count_msg


@pytest.mark.django_db
@mock.patch("apps.news.tasks.redis_client")
@mock.patch("apps.news.tasks.requests.get")
def test_fetch_news_articles_mocks_api_and_redis(
    mock_requests_get, mock_redis
):
    # Fake API response
    mock_response = mock.Mock()
    mock_response.json.return_value = {
        "articles": [
            {
                "title": "Test Article",
                "url": "https://example.com/test",
                "publishedAt": timezone.now().isoformat(),
                "source": {"name": "Mock Source"},
                "content": "Mock content",
                "description": "Mock description",
                "urlToImage": "https://example.com/image.jpg",
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    # Simulate Redis key not existing
    mock_redis.exists.return_value = False

    result = fetch_news_articles()
    assert "News articles fetched and stored successfully." in result
    assert Article.objects.filter(url="https://example.com/test").exists()


def test_redis_heartbeat_does_not_raise():
    with mock.patch("apps.news.tasks.redis_client.ping") as mocked_ping:
        redis_heartbeat()
        mocked_ping.assert_called_once()


def test_cache_articles_adds_only_new_items():
    mock_redis = mock.MagicMock()
    existing = [
        '{"title": "Cached", "url": "https://example.com/cached"}'
    ]
    mock_redis.lrange.return_value = existing

    articles = [
        {"title": "Cached", "url": "https://example.com/cached"},
        {"title": "New One", "url": "https://example.com/new"}
    ]

    with mock.patch("apps.news.tasks.redis_client", mock_redis):
        cache_articles(articles, source="test-source")

    # Only the new article should be pushed to Redis
    pushed = json.loads(mock_redis.lpush.call_args[0][1])
    assert pushed["url"] == "https://example.com/new"


@pytest.mark.django_db
def test_dummy_schedule_creation_for_news_tasks():
    interval = IntervalSchedule.objects.create(
        every=5, period=IntervalSchedule.MINUTES
    )

    task = PeriodicTask.objects.create(
        interval=interval,
        name="Dummy Test: Delete Expired Articles",
        task="apps.news.tasks.delete_expired_articles",
        description="This is a test-only periodic task"
    )

    assert task.task == "apps.news.tasks.delete_expired_articles"
    assert "Dummy Test" in task.name
