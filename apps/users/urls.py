from django.urls import path
from .views import profile_view

app_name = "users"

urlpatterns = [
    # Allauth handles login/signup/logout
    path('profile/', profile_view, name="profile"),
]
