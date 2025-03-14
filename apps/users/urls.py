from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import profile_view, onboarding, test_onboarding, toggle_notifications, mark_notification_read, mark_all_notifications_read

app_name = "users"

urlpatterns = [
    # Allauth handles login/signup/logout
    path('profile/', profile_view, name="profile"),
    # Path to category selection, restricted to logged-in users
    path('onboarding/', login_required(onboarding), name="onboarding"),
    path('toggle_notifications/', toggle_notifications, name='toggle_notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
    path('notifications/mark_all_read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    # Temporary, restricted to logged-in users
    path('test-onboarding/', login_required(test_onboarding), name="test_onboarding"),
]
