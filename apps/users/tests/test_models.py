"""
Test cases for models in the users app.
Covers profile creation, user preferences,
comment and notification creation.
Located in `apps/users/tests/test_models.py`.
"""

import pytest
from django.contrib.auth import get_user_model
from apps.users.models import Profile, Comment, Notification
from apps.news.models import Article, Category, NewsSource

User = get_user_model()


@pytest.mark.django_db
def test_profile_created_on_user_creation():
    user = User.objects.create_user(
      username="alice", email="alice@example.com", password="pass1234"
    )
    assert hasattr(user, "profile")
    assert isinstance(user.profile, Profile)
    assert user.profile.notifications_enabled is True


@pytest.mark.django_db
def test_profile_preferred_categories():
    user = User.objects.create_user(
      username="bob", email="bob@example.com", password="pass1234"
    )
    cat1 = Category.objects.create(name="Tech", slug="tech")
    cat2 = Category.objects.create(name="World", slug="world")

    profile = user.profile
    profile.preferred_categories.set([cat1, cat2])

    assert profile.preferred_categories.count() == 2
    assert cat1 in profile.preferred_categories.all()


@pytest.mark.django_db
def test_comment_creation_and_str_method():
    user = User.objects.create_user(
      username="carol", email="carol@example.com", password="pass1234"
    )
    source = NewsSource.objects.create(name="Test Source", slug="test-source")
    category = Category.objects.create(name="Politics", slug="politics")
    article = Article.objects.create(
        title="Sample Article",
        content="This is a test article.",
        url="http://example.com/article",
        slug="sample-article",
        source=source,
        category=category
    )

    comment = Comment.objects.create(
      user=user, article=article, content="Interesting take!"
    )
    assert str(comment) == f"Comment by {user.username} on {article.title}"


@pytest.mark.django_db
def test_notification_creation_and_defaults():
    user = User.objects.create_user(
      username="dave", email="dave@example.com", password="pass1234"
    )
    notification = Notification.objects.create(
        user=user,
        message="Test notification",
        link="/articles/1/"
    )

    assert notification.user == user
    assert notification.message == "Test notification"
    assert notification.link == "/articles/1/"
    assert notification.read is False
    assert notification.created_at is not None
