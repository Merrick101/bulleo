"""
Test cases for views in the users app.
Covers profile access, updates, preference changes, and deletion.
Located in `apps/users/tests/test_views.py`.
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from apps.news.models import Category, Article

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_with_password():
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    return user


@pytest.fixture
def logged_in_client(user_with_password):
    client = Client()
    client.login(username="testuser", password="testpass123")
    return client


def test_profile_view_requires_login(client):
    response = client.get(reverse("users:profile"))
    assert response.status_code == 302


def test_profile_view_logged_in(logged_in_client):
    response = logged_in_client.get(reverse("users:profile"))
    assert response.status_code == 200
    assert b"Profile Settings" in response.content


def test_update_username(logged_in_client, user_with_password):
    response = logged_in_client.post(
        reverse("users:update_username"),
        {"username": "updateduser"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    user_with_password.refresh_from_db()
    assert user_with_password.username == "updateduser"


def test_update_email(logged_in_client, user_with_password):
    response = logged_in_client.post(
        reverse("users:update_email"),
        {"email": "new@example.com"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    user_with_password.refresh_from_db()
    assert user_with_password.email == "new@example.com"


def test_update_password(logged_in_client, user_with_password):
    response = logged_in_client.post(
        reverse("users:update_password"),
        {
            "current_password": "testpass123",
            "new_password": "newsecurepass456",
            "confirm_new_password": "newsecurepass456",
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    user_with_password.refresh_from_db()
    assert user_with_password.check_password("newsecurepass456")


def test_update_preferences(logged_in_client):
    category = Category.objects.create(name="Tech", slug="tech")
    response = logged_in_client.post(
        reverse("users:preferences_update"),
        {"preferred_categories": [category.id]},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200


def test_remove_saved_article(logged_in_client, user_with_password):
    article = Article.objects.create(
        title="Sample Article",
        content="Some content",
        url="https://example.com/sample",
        slug="sample-article"
    )
    article.saves.add(user_with_password)

    response = logged_in_client.post(
        reverse("users:remove_saved_article"),
        {"id": article.id},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert not article.saves.filter(id=user_with_password.id).exists()


def test_clear_saved_articles(logged_in_client, user_with_password):
    article = Article.objects.create(
        title="Sample Article",
        content="Some content",
        url="https://example.com/sample",
        slug="sample-article"
    )
    article.saves.add(user_with_password)

    response = logged_in_client.post(
        reverse("users:clear_saved_articles"),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert not article.saves.filter(id=user_with_password.id).exists()


def test_remove_upvoted_article(logged_in_client, user_with_password):
    article = Article.objects.create(
        title="Upvoted Article",
        content="Upvote content",
        url="https://example.com/upvote",
        slug="upvoted-article"
    )
    article.likes.add(user_with_password)

    response = logged_in_client.post(
        reverse("users:remove_upvoted_article"),
        {"id": article.id},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert not article.likes.filter(id=user_with_password.id).exists()


def test_clear_upvoted_articles(logged_in_client, user_with_password):
    article = Article.objects.create(
        title="Upvoted Article",
        content="Upvote content",
        url="https://example.com/upvote",
        slug="upvoted-article"
    )
    article.likes.add(user_with_password)

    response = logged_in_client.post(
        reverse("users:clear_upvoted_articles"),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert not article.likes.filter(id=user_with_password.id).exists()


def test_delete_account(logged_in_client, user_with_password):
    response = logged_in_client.post(
        reverse("users:delete_account"),
        {"password": "testpass123"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert not User.objects.filter(username="testuser").exists()
