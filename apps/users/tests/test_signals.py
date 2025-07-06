"""
Tests for user-related signals.
Ensures that a Profile is automatically created for new users.
Located in `apps/users/tests/test_signals.py`.
"""

import pytest
from django.contrib.auth import get_user_model
from apps.users.models import Profile

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_profile_created_on_user_creation():
    user = User.objects.create_user(
        username="signaltestuser",
        email="signal@example.com", password="password123"
    )
    assert Profile.objects.filter(user=user).exists()
