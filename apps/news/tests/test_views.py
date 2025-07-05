import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.news.models import Article, Category, NewsSource
from datetime import datetime
from django.utils.timezone import make_aware


@pytest.fixture
def category():
    return Category.objects.create(name="Technology", slug="technology")


@pytest.fixture
def source():
    return NewsSource.objects.create(name="BBC", slug="bbc")


@pytest.fixture
def article(category, source):
    return Article.objects.create(
        title="Test Article",
        content="Sample content.",
        summary="Short summary.",
        url="https://example.com/test-article",
        slug="test-article",
        source=source,
        category=category,
        published_at=make_aware(datetime.now()),
        imported=True
    )


@pytest.mark.django_db
def test_homepage_view(client):
    url = reverse("news:homepage")
    response = client.get(url)
    assert response.status_code == 200
    assert "trending_chunks" in response.context
    assert "latest_chunks" in response.context


@pytest.mark.django_db
def test_about_view(client):
    url = reverse("news:about")
    response = client.get(url)
    assert response.status_code == 200
    assert "About" in response.content.decode()


@pytest.mark.django_db
def test_search_articles_view(client, article):
    url = reverse("news:search_results") + "?q=test"
    response = client.get(url)
    assert response.status_code == 200
    assert "Test Article" in response.content.decode()


@pytest.mark.django_db
def test_article_detail_view(client, article):
    url = reverse("news:article_detail", args=[article.id])
    response = client.get(url)
    assert response.status_code == 200
    assert article.title in response.content.decode()


@pytest.mark.django_db
def test_toggle_like_authenticated(client, article):
    User.objects.create_user(username="tester", password="pass123")
    client.login(username="tester", password="pass123")
    url = reverse("news:toggle_like", args=[article.id])
    response = client.post(url)
    assert response.status_code == 200
    assert response.json()["liked"] is True


@pytest.mark.django_db
def test_toggle_like_requires_login(client, article):
    url = reverse("news:toggle_like", args=[article.id])
    response = client.post(url)
    assert response.status_code == 302  # redirect to login


@pytest.mark.django_db
def test_toggle_save_authenticated(client, article):
    User.objects.create_user(username="tester2", password="pass123")
    client.login(username="tester2", password="pass123")
    url = reverse("news:toggle_save", args=[article.id])
    response = client.post(url)
    assert response.status_code == 200
    assert response.json()["saved"] is True
