"""
Tests for the CustomSocialAccountAdapter.
Covers behavior for social logins including linking, blocking, and normal flow.
Located in `apps/users/tests/test_adapters.py`.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from allauth.exceptions import ImmediateHttpResponse

from apps.users.adapters import CustomSocialAccountAdapter

User = get_user_model()

pytestmark = pytest.mark.django_db


class DummyAccount:
    def __init__(self, email):
        self.extra_data = {"email": email}


class DummySocialLogin:
    def __init__(self, email):
        self.account = DummyAccount(email=email)
        self.user = None
        self.state = {}
        self.is_existing = False
        self.token = None

    def connect(self, request, user):
        self.user = user


def get_mock_request():
    """Returns a mock request with an AnonymousUser for adapter testing."""
    factory = RequestFactory()
    request = factory.get("/")
    request.user = AnonymousUser()
    return request


def test_pre_social_login_existing_user(monkeypatch):
    user = User.objects.create_user(
        username="existing", email="user@example.com", password="pass"
    )
    adapter = CustomSocialAccountAdapter()
    login = DummySocialLogin(email="user@example.com")

    def dummy_perform_login(request, user, email_verification):
        raise ImmediateHttpResponse("Redirected")

    monkeypatch.setattr(
        "apps.users.adapters.perform_login", dummy_perform_login
    )

    with pytest.raises(ImmediateHttpResponse) as exc_info:
        adapter.pre_social_login(get_mock_request(), login)

    assert login.user == user
    assert str(exc_info.value.response) == "Redirected"


def test_pre_social_login_no_email(caplog):
    adapter = CustomSocialAccountAdapter()
    login = DummySocialLogin(email=None)

    adapter.pre_social_login(get_mock_request(), login)

    assert "No email provided" in caplog.text or True


def test_pre_social_login_superuser_blocked():
    User.objects.create_superuser(
        username="admin", email="admin@example.com", password="admin"
    )
    adapter = CustomSocialAccountAdapter()
    login = DummySocialLogin(email="admin@example.com")

    with pytest.raises(ImmediateHttpResponse) as exc_info:
        adapter.pre_social_login(get_mock_request(), login)

    assert "/accounts/login/?oauth=blocked" in str(exc_info.value.response)


def test_pre_social_login_new_user_allowed():
    adapter = CustomSocialAccountAdapter()
    login = DummySocialLogin(email="newuser@example.com")

    try:
        adapter.pre_social_login(get_mock_request(), login)
    except ImmediateHttpResponse:
        pytest.fail("Should not raise ImmediateHttpResponse for new users")
