from django.urls import path
from .views import profile_view, onboarding, test_onboarding

app_name = "users"

urlpatterns = [
    # Allauth handles login/signup/logout
    path('profile/', profile_view, name="profile"),
    # Path to category selection
    path('onboarding/', onboarding, name="onboarding"),
    # Temporary
    path('test-onboarding/', test_onboarding, name="test_onboarding"),
]
