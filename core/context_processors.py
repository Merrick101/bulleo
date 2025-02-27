from django.contrib.auth.forms import AuthenticationForm
from django import forms
from allauth.account.forms import SignupForm

def auth_forms(request):
    return {
        "login_form": AuthenticationForm(),
        "signup_form": SignupForm(),
    }
