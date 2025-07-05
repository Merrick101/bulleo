"""
Template rendering tests for the News app.
Located at: apps/news/tests/test_templates.py
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.news.models import Article, Category
from apps.users.models import Profile


@pytest.fixture
def user(db):
    user = User.objects.create_user(username="testuser", password="password")
    Profile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def client_logged_in(client, user):
    client.login(username="testuser", password="password")
    return client


@pytest.fixture
def category(db):
    return Category.objects.create(name="Tech", slug="tech")


@pytest.fixture
def article(db, category):
    return Article.objects.create(
        title="AI in 2025",
        content="The future of AI is here.",
        slug="ai-in-2025",
        url="https://example.com/article",
        category=category,
        imported=True
    )


@pytest.mark.django_db
def test_homepage_template_renders(client):
    url = reverse("news:homepage")
    response = client.get(url)
    assert response.status_code == 200
    assert "news/homepage.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_about_template_renders(client):
    url = reverse("news:about")
    response = client.get(url)
    assert response.status_code == 200
    assert "news/about.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_article_detail_template(client, article):
    url = reverse("news:article_detail", args=[article.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "news/article_detail.html" in [t.name for t in response.templates]
    assert "Comment Section" in response.content.decode()


@pytest.mark.django_db
def test_search_template_loads(client):
    url = reverse("news:search_results")
    response = client.get(url, {"q": "AI"})
    assert response.status_code == 200
    assert "news/search_results.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_comment_partial_included(client, article):
    response = client.get(reverse("news:article_detail", args=[article.id]))
    template_names = [t.name for t in response.templates]
    assert "news/_comment.html" in template_names


@pytest.mark.django_db
def test_carousel_partial_present(client):
    response = client.get(reverse("news:homepage"))
    assert "partials/carousel.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_navbar_partials_rendered(client_logged_in):
    response = client_logged_in.get(reverse("news:homepage"))
    names = [t.name for t in response.templates]
    assert "partials/navbar.html" in names
    assert "partials/navbar_authenticated.html" in names


@pytest.mark.django_db
def test_search_form_partial_included(client):
    response = client.get(reverse("news:search_results"))
    assert "partials/search_form.html" in [t.name for t in response.templates]
