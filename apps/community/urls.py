from django.urls import path
from .views import discussion_page

app_name = "community"

urlpatterns = [
    path('', discussion_page, name="discussion"),
]
