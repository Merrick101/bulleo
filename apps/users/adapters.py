"""
Custom adapters for social account login and user connection logic in Bulleo.

This module overrides the default behavior of Django Allauth's
`DefaultSocialAccountAdapter` to control how social logins are handled,
including:

- Automatically linking social accounts to existing users by email
- Preventing social login for superuser accounts
- Redirecting users during the pre-login phase as needed

Used to customize third-party authentication flows (e.g., Google OAuth).
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        print(">>> CustomSocialAccountAdapter fired")

        if request.user.is_authenticated:
            return

        email = sociallogin.account.extra_data.get("email")
        if not email:
            print(">>> No email provided by provider.")
            return

        # Prevent OAuth login for superusers
        if User.objects.filter(email=email, is_superuser=True).exists():
            print(
              ">>> Superuser attempting social login."
              "Redirecting to login page."
            )
            raise ImmediateHttpResponse(
              HttpResponseRedirect("/accounts/login/?oauth=blocked")
            )

        try:
            user = User.objects.get(email=email)
            print(f">>> Found user: {user}")
            sociallogin.connect(request, user)
            raise ImmediateHttpResponse(
                perform_login(request, user, email_verification="optional")
            )
        except User.DoesNotExist:
            print(">>> No existing user. Proceeding with normal flow.")
            pass
