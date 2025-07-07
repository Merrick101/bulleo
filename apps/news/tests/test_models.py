"""
Unit tests for News app models.
Located at: apps/news/tests/test_models.py
"""

import pytest
from django.utils import timezone
from django.urls import reverse
from apps.news.models import Article, Category, NewsSource
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestNewsModels:

    def test_news_source_str(self):
        source = NewsSource.objects.create(name="BBC", slug="bbc")
        assert str(source) == "BBC"

    def test_category_str_and_ordering(self):
        c1 = Category.objects.create(name="Tech", slug="tech", order=2)
        c2 = Category.objects.create(name="Politics", slug="politics", order=1)
        categories = Category.objects.all()
        assert str(c1) == "Tech"
        assert list(categories) == [c2, c1]  # Sorted by order

    def test_article_str_and_get_absolute_url(self):
        user = User.objects.create_user(username="testuser", password="pass")
        category = Category.objects.create(name="Sports", slug="sports")
        source = NewsSource.objects.create(name="Sky News", slug="sky-news")
        article = Article.objects.create(
            title="Match Results",
            content="Team A vs Team B",
            summary="Exciting match!",
            published_at=timezone.now(),
            url="http://example.com/article",
            slug="match-results",
            source=source,
            category=category,
        )
        article.likes.add(user)
        article.saves.add(user)

        assert str(article).startswith("Match Results")
        assert reverse(
            "news:article_detail", args=[article.id]
        ) == article.get_absolute_url()

    def test_article_likes_and_saves(self):
        user1 = User.objects.create_user(username="user1", password="pass")
        user2 = User.objects.create_user(username="user2", password="pass")
        article = Article.objects.create(
            title="Some News",
            content="Details...",
            url="http://test.com",
            slug="some-news"
        )
        article.likes.add(user1, user2)
        article.saves.add(user2)

        assert article.likes.count() == 2
        assert article.saves.count() == 1
