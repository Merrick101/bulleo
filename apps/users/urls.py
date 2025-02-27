from django.urls import path
from .views import login_view, profile_view, signup_view, logout_view

app_name = "users"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path('login/', login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('profile/', profile_view, name="profile"),
]
