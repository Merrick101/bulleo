from django.urls import path
from .views import homepage, article_detail

app_name = "news"

urlpatterns = [
    path('', homepage, name='homepage'),  # News homepage
    path('<int:article_id>/', article_detail, name="article_detail"),
]
