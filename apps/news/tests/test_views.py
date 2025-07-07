"""
Unit tests for views in the News app.
Located at: apps/news/tests/test_views.py
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from apps.news.models import Article, Category, NewsSource
from apps.users.models import Comment


@pytest.fixture
def client(db):
    return Client()


@pytest.fixture
def user(db):
    user = User.objects.create_user(username="testuser", password="password")
    return user


@pytest.fixture
def category(db):
    return Category.objects.create(name="Technology", slug="technology")


@pytest.fixture
def source(db):
    return NewsSource.objects.create(
        name="Example Source", slug="example-source"
    )


@pytest.fixture
def article(db, category, source):
    return Article.objects.create(
        title="Test Article",
        content="Sample content",
        source=source,
        category=category,
        published_at="2024-01-01T00:00:00Z"
    )


@pytest.fixture
def logged_in_client(client, user):
    client.login(username="testuser", password="password")
    return client


def test_homepage_view(client):
    response = client.get(reverse("news:homepage"))
    assert response.status_code == 200
    assert "trending_chunks" in response.context


def test_about_view(client):
    response = client.get(reverse("news:about"))
    assert response.status_code == 200


def test_search_articles_view(client):
    response = client.get(reverse("news:search_results"), {"q": "Test"})
    assert response.status_code == 200
    assert "articles" in response.context


def test_article_detail_view(client, article):
    response = client.get(reverse("news:article_detail", args=[article.id]))
    assert response.status_code == 200
    assert "comments" in response.context


def test_toggle_like(logged_in_client, article):
    response = logged_in_client.post(
        reverse("news:toggle_like", args=[article.id])
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_toggle_save(logged_in_client, article):
    response = logged_in_client.post(
        reverse("news:toggle_save", args=[article.id])
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_post_comment(logged_in_client, article):
    response = logged_in_client.post(
        reverse("news:post_comment", args=[article.id]),
        {"content": "This is a test comment", "parent_comment_id": ""}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_edit_comment(logged_in_client, article, user):
    comment = Comment.objects.create(
        user=user, article=article, content="Old content"
    )
    response = logged_in_client.post(
        reverse("news:edit_comment", args=[comment.id]),
        {"content": "Updated content"}
    )
    assert response.status_code == 200
    assert response.json()["updated_content"] == "Updated content"


def test_delete_comment(logged_in_client, article, user):
    comment = Comment.objects.create(
        user=user, article=article, content="To delete"
    )
    response = logged_in_client.post(
        reverse("news:delete_comment", args=[comment.id])
    )
    assert response.status_code == 200
    assert response.json()["deleted"] is True


def test_reply_to_comment(logged_in_client, article, user):
    parent = Comment.objects.create(
        user=user, article=article, content="Parent"
    )
    response = logged_in_client.post(
        reverse("news:reply_to_comment", args=[article.id, parent.id]),
        {"content": "Replying"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_vote_comment_upvote(logged_in_client, article, user):
    comment = Comment.objects.create(
        user=user, article=article, content="Vote test"
    )
    response = logged_in_client.post(
        reverse("news:vote_comment", args=[comment.id, "upvote"])
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_report_comment(logged_in_client, article, user):
    comment = Comment.objects.create(
        user=user, article=article, content="Report test"
    )
    response = logged_in_client.post(
        reverse("news:report_comment", args=[comment.id])
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
