from django.contrib.auth.forms import AuthenticationForm
from apps.users.forms import CustomUserCreationForm


def auth_forms(request):
    """
    Provides authentication-related forms for modals in base.html,
    using the custom signup form for consistency.
    """
    login_form = AuthenticationForm()
    signup_form = CustomUserCreationForm()

    return {
        "login_form": login_form,
        "signup_form": signup_form,
    }
