"""
Project URL Configuration
Located at: core/urls.py
"""

from django.contrib import admin
from django.conf import settings  # NOQA
from django.urls import path, include
from core.views import custom_logout_redirect
from apps.news.views import homepage

admin.site.index_title = "Admin Dashboard"
admin.site.site_header = "Bulleo Admin"
admin.site.site_title = "Bulleo Admin Panel"

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    path('admin/dashboard/', admin.site.index),
    path(
        "accounts/logout/handler/", custom_logout_redirect,
        name="custom_logout_redirect"
    ),
    path('', include('django.contrib.auth.urls')),

    # Home Page
    path("", homepage, name="home"),

    # Authentication
    path('accounts/', include('allauth.urls')),

    # App-specific
    path('news/', include('apps.news.urls', namespace="news")),
    path("users/", include("apps.users.urls", namespace="users")),
]
