from django.contrib.auth.forms import AuthenticationForm
from apps.users.forms import CustomUserCreationForm  # Import your custom form


def auth_forms(request):
    """
    Provides authentication-related forms in all templates.
    """
    login_form = AuthenticationForm()
    signup_form = CustomUserCreationForm()  # Use your custom signup form

    # Ensure unique IDs for form fields to prevent conflicts in modals
    login_form.fields["username"].widget.attrs["id"] = "id_login_username"
    signup_form.fields["username"].widget.attrs["id"] = "id_signup_username"
    signup_form.fields["email"].widget.attrs["id"] = "id_signup_email"

    return {
        "login_form": login_form,
        "signup_form": signup_form,
    }
