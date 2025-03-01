from django.contrib.auth.forms import AuthenticationForm
from allauth.account.forms import SignupForm


def auth_forms(request):
    """
    Provides authentication-related forms for modals in base.html.
    """
    login_form = AuthenticationForm()
    signup_form = SignupForm()

    return {
        "login_form": login_form,
        "signup_form": signup_form,
    }
