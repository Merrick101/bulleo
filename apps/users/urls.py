"""
User-related URL patterns for the application.
Located at: apps/users/urls.py
"""

from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # Profile management
    path('profile/', views.profile_view,
         name="profile"),
    path('profile/update_username/', views.update_username,
         name='update_username'),
    path('profile/update_email/', views.update_email,
         name='update_email'),
    path('profile/update_password/', views.update_password,
         name='update_password'),

    # Article and comment-related actions
    path("remove-saved-article/", views.remove_saved_article,
         name="remove_saved_article"),
    path("remove-upvoted-article/", views.remove_upvoted_article,
         name="remove_upvoted_article"),
    path("remove-comment/", views.remove_comment,
         name="remove_comment"),
    path("clear-saved-articles/", views.clear_saved_articles,
         name="clear_saved_articles"),
    path("clear-upvoted-articles/", views.clear_upvoted_articles,
         name="clear_upvoted_articles"),
    path("clear-comments/", views.clear_comments,
         name="clear_comments"),

    # Account management
    path("delete-account/", views.delete_account,
         name="delete_account"),

    # Onboarding and preferences
    path('onboarding/', views.onboarding,
         name="onboarding"),
    path('preferences_update/', views.preferences_update,
         name='preferences_update'),

    # Notifications management
    path("notifications/preview/", views.fetch_unread_notifications,
         name="fetch_notifications_preview"),
    path('toggle_notifications/', views.toggle_notifications,
         name='toggle_notifications'),
    path('profile/update_notifications/', views.update_notifications,
         name='update_notifications'),
    path('notifications/mark_all_read/', views.mark_all_notifications_read,
         name='mark_all_notifications_read'),
    path("notifications/mark_read/", views.mark_notification_read,
         name="mark_notification_read"),
    path("notifications/", views.notification_list,
         name="notification_list"),
    path("notifications/clear/", views.clear_notifications,
         name="clear_notifications"),

    # Logout view
    path('logout/', views.logout_view,
         name='logout'),

    # Temporary/test routes
    path('test-onboarding/', views.test_onboarding,
         name="test_onboarding"),

    # Contact form view
    path("contact/", views.contact_view,
         name="contact"),
]
