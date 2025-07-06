"""
Template rendering tests for the users app.
Ensures key templates load with expected content and status codes.
Located in `apps/users/tests/test_templates.py`.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def create_social_app(db):
    site = Site.objects.get_current()
    app = SocialApp.objects.create(
        provider="google",
        name="Google",
        client_id="test-client-id",
        secret="test-secret",
    )
    app.sites.add(site)


@pytest.fixture
def test_user(client):
    user = User.objects.create_user(
        username="tester", password="password123", email="tester@example.com"
    )
    client.login(username="tester", password="password123")
    return user


def test_profile_template_renders(test_user, client):
    response = client.get(reverse("users:profile"))
    assert response.status_code == 200
    assert "Profile Settings" in response.content.decode()
    assert "base.html" in [t.name for t in response.templates]


def test_notifications_template_renders(test_user, client):
    response = client.get(reverse("users:notification_list"))
    assert response.status_code == 200
    assert "Notifications" in response.content.decode()
    assert "base.html" in [t.name for t in response.templates]


def test_signup_template_renders(client):
    response = client.get(reverse("account_signup"))
    assert response.status_code == 200
    assert "Sign Up" in response.content.decode()
    assert "login-signup.css" in response.content.decode()


def test_login_template_renders(client):
    SocialApp.objects.get_or_create(
        provider="google",
        name="Google",
        client_id="dummy-id",
        secret="dummy-secret"
    )

    response = client.get(reverse("account_login"))
    assert response.status_code == 200
    assert "Log In" in response.content.decode()
    assert "login-signup.css" in response.content.decode()


def test_logout_template_renders(client):
    User.objects.create_user(username="temp", password="temp123")
    client.login(username="temp", password="temp123")
    response = client.get(reverse("account_logout"))

    assert response.status_code == 200
    html = response.content.decode()
    assert "Log Out" in html or "Confirm" in html or "Are you sure" in html


def test_socialaccount_signup_template_renders(client):
    SocialApp.objects.get_or_create(
        provider="google",
        name="Google",
        client_id="dummy-id",
        secret="dummy-secret"
    )

    response = client.get("/accounts/social/signup/", follow=True)
    assert response.status_code in [200, 302]
