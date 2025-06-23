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


def notifications_processor(request):
    if request.user.is_authenticated:
        notifications = request.user.notifications.filter(read=False)
    else:
        notifications = []
    return {'notifications': notifications}
