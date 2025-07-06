"""
Test cases for forms in the users app.
Validates correct behavior of form validation and clean methods.
Located in `apps/users/tests/test_forms.py`.
"""

import pytest
from apps.users.forms import (
    CommentForm,
    UpdateEmailForm,
    UpdatePasswordForm,
)

pytestmark = pytest.mark.django_db


def test_valid_comment_form():
    form = CommentForm(data={"content": "This is a test comment."})
    assert form.is_valid()


def test_empty_comment_form_invalid():
    form = CommentForm(data={"content": ""})
    assert not form.is_valid()
    assert "content" in form.errors


def test_update_email_form_valid():
    form = UpdateEmailForm(data={"email": "newemail@example.com"})
    assert form.is_valid()


def test_update_email_form_invalid():
    form = UpdateEmailForm(data={"email": "invalid-email"})
    assert not form.is_valid()
    assert "email" in form.errors


def test_update_password_form_matching_passwords_valid():
    form = UpdatePasswordForm(
        data={
            "current_password": "oldpass123",
            "new_password": "newpass456",
            "confirm_new_password": "newpass456"
        }
    )
    assert form.is_valid()


def test_update_password_form_mismatch_invalid():
    form = UpdatePasswordForm(
        data={
            "current_password": "oldpass123",
            "new_password": "newpass456",
            "confirm_new_password": "different456"
        }
    )
    assert not form.is_valid()
    assert "confirm_new_password" in form.errors
