from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    login_view,
    logout_view,
    signup_view,
    profile_view,
    check_login_status
)

app_name = "users"

urlpatterns = [
    # User Authentication URLs
    path('login/', login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path('profile/', profile_view, name="profile"),

    # Login status check
    path("check-login-status/", check_login_status, name="check_login_status"),

    # Password Reset URLs
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
