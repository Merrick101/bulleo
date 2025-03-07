import json
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock
from requests.models import Response
from django.test import TestCase
from django.utils import timezone

import requests
from apps.news.models import Article, NewsSource
from apps.news.tasks import fetch_news_articles, fetch_guardian_articles
from apps.users.models import Category


logger = logging.getLogger(__name__)


def create_mock_response(json_data, status_code=200):
    """
    Helper function to create a mock Response object.
    """
    response = Response()
    response.status_code = status_code
    response._content = json.dumps(json_data).encode("utf-8")
    return response


class FetchNewsArticlesTaskTest(TestCase):
    def setUp(self):
        """Clear the database before each test."""
        Article.objects.all().delete()
        NewsSource.objects.all().delete()

    @patch("apps.news.tasks.redis_client", new_callable=MagicMock)  # Mock Redis
    @patch("apps.news.tasks.requests.get")
    def test_fetch_news_articles_success(self, mock_get, mock_redis):
        """Test that fetch_news_articles successfully creates an article."""
        mock_redis.exists.return_value = False  # Pretend Redis is empty
        mock_redis.lrange.return_value = []  # No cached articles

        dummy_response = {
            "articles": [
                {
                    "title": "Test Article",
                    "content": "This is test article content.",
                    "description": "Test article description.",
                    "urlToImage": "http://example.com/image.jpg",
                    "publishedAt": "2025-03-05T12:00:00Z",
                    "url": "http://example.com/article",
                    "source": {"name": "Test Source"},
                }
            ]
        }
        mock_get.return_value = create_mock_response(dummy_response)

        fetch_news_articles()

        self.assertEqual(Article.objects.count(), 1)
        article = Article.objects.first()
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.source.name, "Test Source")

    @patch("apps.news.tasks.redis_client", new_callable=MagicMock)
    @patch("apps.news.tasks.requests.get")
    def test_fetch_news_articles_api_failure(self, mock_get, mock_redis):
        """Test that API failure logs and does not create articles."""
        mock_redis.exists.return_value = False
        mock_get.side_effect = requests.RequestException("API error")

        result = fetch_news_articles()

        self.assertIn("Error fetching articles", result)
        self.assertEqual(Article.objects.count(), 0)

    @patch("apps.news.tasks.redis_client", new_callable=MagicMock)
    @patch("apps.news.tasks.requests.get")
    def test_fetch_news_articles_no_duplicates(self, mock_get, mock_redis):
        """Ensure articles with the same URL are not duplicated."""
        mock_redis.exists.return_value = False
        mock_redis.lrange.return_value = []

        dummy_response = {
            "articles": [
                {
                    "title": "Duplicate Article",
                    "content": "Content",
                    "urlToImage": "http://example.com/image.jpg",
                    "publishedAt": "2025-03-05T12:00:00Z",
                    "url": "http://example.com/duplicate-article",
                    "source": {"name": "Duplicate Source"},
                }
            ]
        }
        mock_get.return_value = create_mock_response(dummy_response)

        fetch_news_articles()
        fetch_news_articles()  # Call again to check duplicate handling

        self.assertEqual(Article.objects.count(), 1)

    @patch("apps.news.tasks.redis_client", new_callable=MagicMock)
    @patch("apps.news.tasks.requests.get")
    def test_fetch_news_articles_invalid_date(self, mock_get, mock_redis):
        """Test handling of invalid publishedAt dates."""
        mock_redis.exists.return_value = False

        dummy_response = {
            "articles": [
                {
                    "title": "Invalid Date Article",
                    "content": "Content",
                    "publishedAt": "InvalidDateString",
                    "url": "http://example.com/invalid-date",
                    "source": {"name": "Invalid Source"},
                }
            ]
        }
        mock_get.return_value = create_mock_response(dummy_response)

        fetch_news_articles()
        article = Article.objects.first()

        self.assertIsInstance(article.published_at, datetime)

    @patch("apps.news.tasks.redis_client", new_callable=MagicMock)
    @patch("apps.news.tasks.requests.get")
    def test_fetch_news_articles_timeout(self, mock_get, mock_redis):
        """Test handling of request timeout."""
        mock_redis.exists.return_value = False
        mock_get.side_effect = requests.Timeout

        result = fetch_news_articles()

        self.assertIn("Error fetching articles", result)


class FetchGuardianArticlesTaskTest(TestCase):
    def setUp(self):
        """Clear database and create test category."""
        Article.objects.all().delete()
        NewsSource.objects.all().delete()
        Category.objects.all().delete()
        self.test_category = Category.objects.create(name="World News", slug="world-news")

    @patch("apps.news.tasks.redis_client", new_callable=MagicMock)
    @patch("apps.news.tasks.requests.get")
    def test_fetch_guardian_articles_success(self, mock_get, mock_redis):
        """Test that fetch_guardian_articles successfully creates articles."""
        mock_redis.exists.return_value = False
        mock_redis.lrange.return_value = []

        dummy_response = {
            "response": {
                "results": [
                    {
                        "webTitle": "Guardian Test Article",
                        "webUrl": "http://example.com/guardian-article",
                        "webPublicationDate": "2025-03-05T12:00:00Z",
                        "fields": {
                            "trailText": "Guardian article summary.",
                            "thumbnail": "http://example.com/guardian-thumbnail.jpg",
                        },
                    }
                ]
            }
        }
        mock_get.return_value = create_mock_response(dummy_response)

        fetch_guardian_articles()

        self.assertEqual(Article.objects.count(), 1)
        article = Article.objects.first()
        self.assertEqual(article.title, "Guardian Test Article")
        self.assertEqual(article.source.name, "The Guardian")
        self.assertEqual(article.category, self.test_category)

    @patch("apps.news.tasks.redis_client", new_callable=MagicMock)
    @patch("apps.news.tasks.requests.get")
    def test_fetch_guardian_articles_api_failure(self, mock_get, mock_redis):
        """Test that API failure logs and does not create articles."""
        mock_redis.exists.return_value = False
        mock_get.side_effect = requests.RequestException("API error")

        result = fetch_guardian_articles()

        self.assertIn("Guardian fetch complete. Total new articles created: 0", result)
        self.assertEqual(Article.objects.count(), 0)

    @patch("apps.news.tasks.redis_client", new_callable=MagicMock)
    @patch("apps.news.tasks.requests.get")
    def test_fetch_guardian_articles_missing_fields(self, mock_get, mock_redis):
        """Test handling when some fields are missing in API response."""
        mock_redis.exists.return_value = False

        dummy_response = {
            "response": {
                "results": [
                    {
                        "webTitle": "Missing Fields Article",
                        "webUrl": "http://example.com/missing-fields",
                        "webPublicationDate": "2025-03-05T12:00:00Z"
                        # No "fields" key
                    }
                ]
            }
        }
        mock_get.return_value = create_mock_response(dummy_response)

        fetch_guardian_articles()
        article = Article.objects.first()

        self.assertEqual(article.summary, "")
        self.assertEqual(article.image_url, "")
