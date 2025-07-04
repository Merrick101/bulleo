"""
Context processors for the core application.
Located at: core/context_processors.py
"""

from django.contrib.auth.forms import AuthenticationForm
from allauth.account.forms import SignupForm


def auth_forms(request):
    login_form = AuthenticationForm()
    signup_form = SignupForm()
    return {
        "login_form": login_form,
        "signup_form": signup_form,
    }


def notifications_unread_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            count = request.user.notifications.filter(read=False).count()
    except Exception:
        pass
    return {"notifications_unread_count": count}
