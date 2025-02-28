from django.urls import path
from .views import login_view, logout_view, signup_view, profile_view, close_popup, oauth_callback, check_login_status
from django.contrib.auth import views as auth_views

app_name = "users"

urlpatterns = [
    # User Authentication URLs
    path('login/', login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path('profile/', profile_view, name="profile"),
    # Close Popup URL
    path("close-popup/", close_popup, name="close_popup"),
    path("oauth/callback/", oauth_callback, name="oauth_callback"),
    path("check-login-status/", check_login_status, name="check_login_status"),
    # Password Reset URLs
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
