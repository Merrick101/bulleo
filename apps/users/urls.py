from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = "users"

urlpatterns = [
    # Allauth handles login/signup/logout
    path('profile/', views.profile_view, name="profile"),
    path('profile/update_username/', views.update_username, name='update_username'),
    path('profile/update_email/', views.update_email, name='update_email'),
    path('profile/update_password/', views.update_password, name='update_password'),
    path('profile/update_notifications/', views.update_notifications, name='update_notifications'),

    # Article and comment-related actions
    path("remove-saved-article/", views.remove_saved_article, name="remove_saved_article"),
    path("remove-upvoted-article/", views.remove_upvoted_article, name="remove_upvoted_article"),
    path("remove-comment/", views.remove_comment, name="remove_comment"),
    path("clear-saved-articles/", views.clear_saved_articles, name="clear_saved_articles"),
    path("clear-upvoted-articles/", views.clear_upvoted_articles, name="clear_upvoted_articles"),
    path("clear-comments/", views.clear_comments, name="clear_comments"),

    # Account management
    path("delete-account/", views.delete_account, name="delete_account"),

    # User preferences and notifications
    path('onboarding/', views.onboarding, name="onboarding"),
    path('preferences_update/', views.preferences_update, name='preferences_update'),
    path('toggle_notifications/', views.toggle_notifications, name='toggle_notifications'),
    path('notifications/mark_all_read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Logout view
    path('logout/', views.logout_view, name='logout'),

    # Temporary/test routes
    path('test-onboarding/', views.test_onboarding, name="test_onboarding"),
]
