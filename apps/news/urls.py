"""
URL configuration for the news application.
This module defines the URL patterns for the news app, including views
for the homepage, article details, comments, and user interactions.
Located at: apps/news/urls.py
"""

from django.urls import path
from .views import (
    homepage, search_articles, article_detail, vote_comment, post_comment,
    edit_comment, delete_comment, reply_to_comment, report_comment,
    toggle_like, toggle_save, about_view
)

app_name = "news"

urlpatterns = [
    path('', homepage, name='homepage'),
    path('about/', about_view, name='about'),
    path('search/', search_articles, name='search_results'),
    path(
        'article/<int:article_id>/',
        article_detail,
        name='article_detail'
    ),
    path(
        'articles/<int:article_id>/toggle_like/',
        toggle_like,
        name='toggle_like'
    ),
    path(
        'articles/<int:article_id>/toggle_save/',
        toggle_save,
        name='toggle_save'
    ),
    path(
        'article/<int:article_id>/comment/',
        post_comment,
        name='post_comment'
    ),
    path(
        'comment/<int:comment_id>/vote/<str:action>/',
        vote_comment,
        name='vote_comment'
    ),
    path(
        'comment/<int:comment_id>/edit/',
        edit_comment,
        name='edit_comment'
    ),
    path(
        'comment/<int:comment_id>/delete/',
        delete_comment,
        name='delete_comment'
    ),
    path(
        'article/<int:article_id>/comment/<int:parent_comment_id>/reply/',
        reply_to_comment,
        name='reply_to_comment'
    ),
    path(
        'comment/<int:comment_id>/report/',
        report_comment,
        name='report_comment'
    ),
]
