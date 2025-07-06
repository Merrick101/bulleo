"""
Tests for the notifications system in the users app.
Covers Notification model behavior, Signal-based notification creation,
Notification views (list, mark as read/unread),
Context processor for navbar previews.
Located in `apps/users/tests/test_notifications.py`.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.news.models import Article, Category
from apps.users.models import Notification


User = get_user_model()


@pytest.mark.django_db
def test_notification_creation():
    user = User.objects.create_user(
      username="bob", email="bob@test.com", password="pass123"
    )
    notif = Notification.objects.create(user=user, verb="Test notification")

    assert notif.pk is not None
    assert notif.read is False
    assert notif.verb == "Test notification"
    assert notif.user == user


@pytest.mark.django_db
def test_notification_str_representation():
    user = User.objects.create_user(
      username="alice", email="alice@test.com", password="pass123"
    )
    notif = Notification.objects.create(user=user, verb="Something happened")

    assert str(
      notif
    ) == f"Notification for {user.username}: Something happened"


@pytest.mark.django_db
def test_mark_all_read_view(client, django_user_model):
    user = django_user_model.objects.create_user(
      username="markuser", password="pass123"
    )
    Notification.objects.create(user=user, verb="1")
    Notification.objects.create(user=user, verb="2")

    client.force_login(user)
    response = client.post(
      reverse("users:mark_all_read"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    assert Notification.objects.filter(user=user, read=True).count() == 2


@pytest.mark.django_db
def test_mark_single_notification_read(client):
    user = User.objects.create_user(username="solo", password="pass123")
    notif = Notification.objects.create(user=user, verb="Ping!")

    client.force_login(user)
    response = client.post(
        reverse("users:mark_read"),
        {"id": notif.id},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    notif.refresh_from_db()
    assert notif.read is True


@pytest.mark.django_db
def test_notifications_preview_view(client):
    user = User.objects.create_user(username="previewer", password="pass123")
    Notification.objects.create(user=user, verb="Preview this!")
    client.force_login(user)

    response = client.get(
      reverse("users:notification_preview"),
      HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert "success" in response.json()
    assert "html" in response.json()


@pytest.mark.django_db
def test_notifications_list_view_authenticated(client):
    user = User.objects.create_user(username="reader", password="pass123")
    client.force_login(user)
    Notification.objects.create(user=user, verb="You got a ping")

    response = client.get(reverse("users:notifications"))
    assert response.status_code == 200
    assert "Notifications" in response.content.decode()


@pytest.mark.django_db
def test_notification_sent_to_users_with_matching_preferences():
    # Create category
    politics = Category.objects.create(name="Politics", slug="politics")

    # Create two users
    user1 = User.objects.create_user(username="alice", password="test123")
    user2 = User.objects.create_user(username="bob", password="test123")

    # Attach preferred categories to only one user
    profile1 = user1.profile
    profile1.preferred_categories.add(politics)

    # user2 doesn't have the category in preferences
    profile2 = user2.profile
    assert politics not in profile2.preferred_categories.all()

    # Create article in "Politics" category
    Article.objects.create(
        title="Election News",
        content="A big update in politics...",
        summary="Summary",
        url="https://example.com/election-news",
        slug="election-news",
        category=politics
    )

    # Check notifications
    assert Notification.objects.filter(user=user1).exists()
    assert not Notification.objects.filter(user=user2).exists()
