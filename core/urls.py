from django.contrib import admin
from django.urls import path, include
from apps.news.views import homepage

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),

    # Application URLs
    path("", homepage, name="home"),
    path('news/', include('apps.news.urls', namespace="news")),
    path("users/", include("apps.users.urls", namespace="users")),
]
