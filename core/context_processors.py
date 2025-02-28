from django.contrib.auth.forms import AuthenticationForm
from allauth.account.forms import SignupForm


def auth_forms(request):
    """
    Provides authentication-related forms in all templates.
    """
    login_form = AuthenticationForm()
    signup_form = SignupForm()

    # Ensure unique IDs for form fields
    login_form.fields["username"].widget.attrs["id"] = "id_login_username"
    signup_form.fields["username"].widget.attrs["id"] = "id_signup_username"

    return {
        "login_form": login_form,
        "signup_form": signup_form,
    }
