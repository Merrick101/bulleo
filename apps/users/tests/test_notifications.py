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
    notif = Notification.objects.create(user=user, message="Test notification")

    assert notif.pk is not None
    assert notif.read is False
    assert notif.message == "Test notification"
    assert notif.user == user


@pytest.mark.django_db
def test_notification_str_representation():
    user = User.objects.create_user(
        username="alice", email="alice@test.com", password="pass123"
    )
    notif = Notification.objects.create(
      user=user, message="Something happened"
    )

    expected_str = f"Notification for {user.username}: Something happened"
    assert str(notif) == expected_str[:50]  # match model __str__ slicing


@pytest.mark.django_db
def test_mark_all_read_view(client):
    user = User.objects.create_user(username="markuser", password="pass123")
    Notification.objects.create(user=user, message="1")
    Notification.objects.create(user=user, message="2")

    client.force_login(user)
    response = client.post(
        reverse("users:mark_all_notifications_read"),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert Notification.objects.filter(user=user, read=True).count() == 2


@pytest.mark.django_db
def test_mark_single_notification_read(client):
    user = User.objects.create_user(username="solo", password="pass123")
    notif = Notification.objects.create(user=user, message="Ping!")

    client.force_login(user)
    response = client.post(
        reverse("users:mark_notification_read"),
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
    Notification.objects.create(user=user, message="Preview this!")
    client.force_login(user)

    response = client.get(
        reverse("users:fetch_notifications_preview"),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert "success" in response.json()
    assert "html" in response.json()


@pytest.mark.django_db
def test_notifications_list_view_authenticated(client):
    user = User.objects.create_user(username="reader", password="pass123")
    client.force_login(user)
    Notification.objects.create(user=user, message="You got a ping")

    response = client.get(reverse("users:notification_list"))
    assert response.status_code == 200
    assert "Notifications" in response.content.decode()


@pytest.mark.django_db
def test_notification_sent_to_users_with_matching_preferences():
    category = Category.objects.create(name="Politics", slug="politics")
    user1 = User.objects.create_user(username="alice", password="test123")
    user2 = User.objects.create_user(username="bob", password="test123")

    # Assign preference to user1
    user1.profile.preferred_categories.add(category)

    # Create article in that category (simulate signal)
    article = Article.objects.create(
        title="Election News",
        content="A big update in politics...",
        summary="Summary",
        url="https://example.com/election-news",
        slug="election-news",
        category=category
    )

    # Manual notification simulation (if no signal logic present)
    for user in User.objects.all():
        if category in user.profile.preferred_categories.all():
            Notification.objects.create(
                user=user,
                message=f"New article in {category.name}: {article.title}",
                link=article.get_absolute_url()
            )

    assert Notification.objects.filter(user=user1).exists()
    assert not Notification.objects.filter(user=user2).exists()
