from django.urls import path
from .views import homepage, article_detail, article_list

app_name = "news"

urlpatterns = [
    path('', homepage, name='homepage'),  # News homepage
    path("articles/", article_list, name="article_list"),
    path('<int:article_id>/', article_detail, name="article_detail"),
]
