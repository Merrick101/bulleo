from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from apps.news.views import homepage

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),

    # Use Allauth for authentication (removing django.contrib.auth.urls)
    path('accounts/', include('allauth.urls')),

    # Application URLs
    path("", homepage, name="home"),
    path('news/', include('apps.news.urls', namespace="news")),
    path("users/", include("apps.users.urls", namespace="users")),
]
