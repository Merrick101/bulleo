"""
Test cases for forms in the users app.
Validates correct behavior of form validation and clean methods.
Located in `apps/users/tests/test_forms.py`.
"""

import pytest
from django.contrib.auth import get_user_model
from apps.users.forms import (
    CustomUserCreationForm,
    ProfileForm,
    NewsPreferencesForm,
    DeleteAccountForm,
    CommentForm,
    ContactForm
)
from apps.news.models import Category, Article
from apps.users.models import Comment, Profile  # NOQA

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_custom_user_creation_form_valid():
    form = CustomUserCreationForm(data={
        "username": "testuser",
        "email": "test@example.com",
        "password1": "strongpassword123",
        "password2": "strongpassword123"
    })
    assert form.is_valid()


def test_custom_user_creation_form_email_required():
    form = CustomUserCreationForm(data={
        "username": "testuser",
        "email": "",
        "password1": "strongpassword123",
        "password2": "strongpassword123"
    })
    assert not form.is_valid()
    assert "email" in form.errors


def test_profile_form_fields_exist():
    form = ProfileForm()
    assert "bio" in form.fields
    assert "preferred_categories" in form.fields


@pytest.mark.django_db
def test_news_preferences_form_valid():
    # Create user first, which should automatically create a Profile
    user = User.objects.create_user(username="prefuser", password="pass123")

    # Create a category to be selected
    category = Category.objects.create(name="Tech", slug="tech")

    # Fetch the associated profile (auto-created)
    profile = user.profile

    # Instantiate form with POST data and the profile instance
    form = NewsPreferencesForm(
        instance=profile,
        data={"preferred_categories": [category.id]}
    )

    # Validate form
    assert form.is_valid(), form.errors

    # Save and assert the category was set
    form.save()
    assert category in profile.preferred_categories.all()


def test_delete_account_form_requires_password():
    form = DeleteAccountForm(data={"password": ""})
    assert not form.is_valid()
    assert "password" in form.errors


def test_valid_comment_form():
    user = User.objects.create_user(username="alice", password="pass")
    article = Article.objects.create(
        title="Test Article",
        content="Content",
        summary="Summary",
        url="https://example.com",
        slug="test-article"
    )
    form = CommentForm(
        user=user,
        article=article,
        data={"content": "A great article!"}
    )
    assert form.is_valid()


def test_duplicate_comment_blocked():
    user = User.objects.create_user(username="bob", password="pass")
    article = Article.objects.create(
        title="Another Article",
        content="Body",
        summary="Summary",
        url="https://example.com/2",
        slug="article-2"
    )
    Comment.objects.create(user=user, article=article, content="Nice read!")

    form = CommentForm(
        user=user,
        article=article,
        data={"content": "Nice read!"}
    )
    assert not form.is_valid()


def test_contact_form_valid():
    form = ContactForm(data={
        "name": "Alice",
        "email": "alice@example.com",
        "subject": "Feedback",
        "message": "Great site!"
    })
    assert form.is_valid()


def test_contact_form_missing_message_invalid():
    form = ContactForm(data={
        "name": "Bob",
        "email": "bob@example.com",
        "subject": "Hi",
        "message": ""
    })
    assert not form.is_valid()
    assert "message" in form.errors
