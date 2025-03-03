from django.urls import path
from .views import homepage, search_articles, article_detail

app_name = "news"

urlpatterns = [
    path('', homepage, name='homepage'),
    path("search/", search_articles, name="search_results"),
    path('article/<int:article_id>/', article_detail, name="article_detail"),
]
