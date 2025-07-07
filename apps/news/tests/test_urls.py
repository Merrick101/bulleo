"""
URL routing tests for the News app.
Located at: apps/news/tests/test_urls.py
"""

from django.urls import reverse, resolve
from apps.news import views


def test_homepage_url_resolves():
    path = reverse("news:homepage")
    assert resolve(path).func == views.homepage


def test_about_url_resolves():
    path = reverse("news:about")
    assert resolve(path).func == views.about_view


def test_search_url_resolves():
    path = reverse("news:search_results")
    assert resolve(path).func == views.search_articles


def test_article_detail_url_resolves():
    path = reverse("news:article_detail", kwargs={"article_id": 1})
    assert resolve(path).func == views.article_detail


def test_toggle_like_url_resolves():
    path = reverse("news:toggle_like", kwargs={"article_id": 1})
    assert resolve(path).func == views.toggle_like


def test_toggle_save_url_resolves():
    path = reverse("news:toggle_save", kwargs={"article_id": 1})
    assert resolve(path).func == views.toggle_save


def test_post_comment_url_resolves():
    path = reverse("news:post_comment", kwargs={"article_id": 1})
    assert resolve(path).func == views.post_comment


def test_vote_comment_url_resolves():
    path = reverse(
        "news:vote_comment", kwargs={"comment_id": 1, "action": "upvote"}
    )
    assert resolve(path).func == views.vote_comment


def test_edit_comment_url_resolves():
    path = reverse("news:edit_comment", kwargs={"comment_id": 1})
    assert resolve(path).func == views.edit_comment


def test_delete_comment_url_resolves():
    path = reverse("news:delete_comment", kwargs={"comment_id": 1})
    assert resolve(path).func == views.delete_comment


def test_reply_to_comment_url_resolves():
    path = reverse(
        "news:reply_to_comment", kwargs={
            "article_id": 1, "parent_comment_id": 2
        }
    )
    assert resolve(path).func == views.reply_to_comment


def test_report_comment_url_resolves():
    path = reverse("news:report_comment", kwargs={"comment_id": 1})
    assert resolve(path).func == views.report_comment
