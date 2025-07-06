"""
URL tests for the users app.
Located in `apps/users/tests/test_urls.py`.
"""

import pytest
from django.urls import reverse, resolve
from apps.users import views

pytestmark = pytest.mark.django_db


def test_profile_url_resolves():
    path = reverse("users:profile")
    assert resolve(path).func == views.profile_view


def test_update_username_url_resolves():
    path = reverse("users:update_username")
    assert resolve(path).func == views.update_username


def test_update_email_url_resolves():
    path = reverse("users:update_email")
    assert resolve(path).func == views.update_email


def test_update_password_url_resolves():
    path = reverse("users:update_password")
    assert resolve(path).func == views.update_password


def test_preferences_update_url_resolves():
    path = reverse("users:preferences_update")
    assert resolve(path).func == views.preferences_update


def test_remove_saved_article_url_resolves():
    path = reverse("users:remove_saved_article")
    assert resolve(path).func == views.remove_saved_article


def test_remove_upvoted_article_url_resolves():
    path = reverse("users:remove_upvoted_article")
    assert resolve(path).func == views.remove_upvoted_article


def test_remove_comment_url_resolves():
    path = reverse("users:remove_comment")
    assert resolve(path).func == views.remove_comment


def test_clear_saved_articles_url_resolves():
    path = reverse("users:clear_saved_articles")
    assert resolve(path).func == views.clear_saved_articles


def test_clear_upvoted_articles_url_resolves():
    path = reverse("users:clear_upvoted_articles")
    assert resolve(path).func == views.clear_upvoted_articles


def test_clear_comments_url_resolves():
    path = reverse("users:clear_comments")
    assert resolve(path).func == views.clear_comments


def test_delete_account_url_resolves():
    path = reverse("users:delete_account")
    assert resolve(path).func == views.delete_account


def test_toggle_notifications_url_resolves():
    path = reverse("users:toggle_notifications")
    assert resolve(path).func == views.toggle_notifications


def test_notifications_list_url_resolves():
    path = reverse("users:notification_list")
    assert resolve(path).func == views.notification_list


def test_mark_notification_read_url_resolves():
    path = reverse("users:mark_notification_read")
    assert resolve(path).func == views.mark_notification_read


def test_mark_all_notifications_read_url_resolves():
    path = reverse("users:mark_all_notifications_read")
    assert resolve(path).func == views.mark_all_notifications_read


def test_notification_preview_url_resolves():
    path = reverse("users:fetch_notifications_preview")
    assert resolve(path).func == views.fetch_unread_notifications
