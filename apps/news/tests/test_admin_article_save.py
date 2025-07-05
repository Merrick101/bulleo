"""
Admin form save test for Article model.
Located at: apps/news/tests/test_admin_article_save.py
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from apps.news.models import Article, Category, NewsSource


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin", password="adminpass", email="admin@example.com"
    )


@pytest.fixture
def admin_client(admin_user, client):
    client.login(username="admin", password="adminpass")
    return client


@pytest.fixture
def category(db):
    return Category.objects.create(name="World", slug="world")


@pytest.fixture
def source(db):
    return NewsSource.objects.create(name="Reuters", slug="reuters")


def test_article_creation_via_admin(admin_client, category, source):
    url = reverse("admin:apps_news_article_add")
    data = {
        "title": "Admin Created Article",
        "slug": "admin-created-article",
        "content": "This is a test article created via admin.",
        "summary": "Test summary",
        "image_url": "https://example.com/image.jpg",
        "published_at_0": timezone.now().strftime("%Y-%m-%d"),
        "published_at_1": timezone.now().strftime("%H:%M:%S"),
        "url": "https://example.com/article",
        "views": 0,
        "source": source.id,
        "category": category.id,
        "_save": "Save",  # Simulates clicking "Save" in admin
    }
    response = admin_client.post(url, data, follow=True)
    assert response.status_code == 200
    assert Article.objects.filter(title="Admin Created Article").exists()
