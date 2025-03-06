from django.urls import path
from .views import homepage, search_articles, article_detail, vote_comment, post_comment

app_name = "news"

urlpatterns = [
    path('', homepage, name='homepage'),
    path("search/", search_articles, name="search_results"),
    path('article/<int:article_id>/', article_detail, name="article_detail"),
    path("article/<int:article_id>/comment/", post_comment, name="post_comment"),
    path("comment/<int:comment_id>/vote/<str:action>/", vote_comment, name="vote_comment"),
]
