"""
Tests for the Django admin interface of the Users app.
Covers custom model registration and admin configurations.
Located in `apps/users/tests/test_admin.py`.
"""

from django.contrib import admin
from apps.users.models import Profile


def test_profile_model_registered_in_admin():
    """Ensure the Profile model is registered with the Django admin site."""
    assert Profile in admin.site._registry
