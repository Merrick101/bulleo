import json
import requests
from datetime import datetime
from dateutil import parser
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock

from apps.news.models import Article, NewsSource
from apps.users.models import Category
from apps.news.tasks import fetch_news_articles, fetch_guardian_articles


class FetchNewsArticlesTaskTest(TestCase):
    @patch('apps.news.tasks.requests.get')
    def test_fetch_news_articles_success(self, mock_get):
        # Create a dummy JSON response for News API
        dummy_response = {
            "articles": [
                {
                    "title": "Test Article",
                    "content": "This is test article content.",
                    "description": "Test article description.",
                    "urlToImage": "http://example.com/image.jpg",
                    "publishedAt": "2025-03-05T12:00:00Z",
                    "url": "http://example.com/article",
                    "source": {"name": "Test Source"}
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = dummy_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        # Call the task synchronously for testing
        result = fetch_news_articles.delay()
        result_message = result.get(timeout=10)

        self.assertIn("News articles fetched and stored successfully", result_message)
        self.assertEqual(Article.objects.count(), 1)
        article = Article.objects.first()
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.source.name, "Test Source")

    @patch('apps.news.tasks.requests.get')
    def test_fetch_news_articles_api_failure(self, mock_get):
        # Simulate an API error by having requests.get raise a RequestException.
        mock_get.side_effect = requests.RequestException("API error")
        result = fetch_news_articles.delay()
        result_message = result.get(timeout=10)
        self.assertIn("Error fetching articles from News API", result_message)
        self.assertEqual(Article.objects.count(), 0)


class FetchGuardianArticlesTaskTest(TestCase):
    @patch('apps.news.tasks.requests.get')
    def test_fetch_guardian_articles_success(self, mock_get):
        # Create a dummy JSON response for the Guardian API
        dummy_response = {
            "response": {
                "results": [
                    {
                        "webTitle": "Guardian Test Article",
                        "webUrl": "http://example.com/guardian-article",
                        "webPublicationDate": "2025-03-05T12:00:00Z",
                        "fields": {
                            "trailText": "Guardian article summary.",
                            "thumbnail": "http://example.com/guardian-thumbnail.jpg"
                        }
                    }
                ]
            }
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = dummy_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        # Ensure that the category mapping works (if your task is using Category lookup)
        Category.objects.create(name="World News", slug="world-news")

        result = fetch_guardian_articles.delay()
        result_message = result.get(timeout=10)
        self.assertIn("Guardian fetch complete", result_message)
        self.assertEqual(Article.objects.count(), 1)
        article = Article.objects.first()
        self.assertEqual(article.title, "Guardian Test Article")
        self.assertEqual(article.source.name, "The Guardian")

    @patch('apps.news.tasks.requests.get')
    def test_fetch_guardian_articles_api_failure(self, mock_get):
        # Simulate an API error by having requests.get raise a RequestException.
        mock_get.side_effect = requests.RequestException("API error")
        result = fetch_guardian_articles.delay()
        result_message = result.get(timeout=10)
        self.assertIn("Error fetching Guardian articles", result_message)
        self.assertEqual(Article.objects.count(), 0)
