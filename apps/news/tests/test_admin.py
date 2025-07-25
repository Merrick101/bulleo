"""
Unit tests for News app admin configuration.
Located at: apps/news/tests/test_admin.py
"""

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import strip_tags
from apps.news.models import Article, NewsSource, Category
from apps.news.admin import ArticleAdmin, NewsSourceAdmin, CategoryAdmin
from django_celery_beat.models import PeriodicTask, IntervalSchedule


@pytest.fixture
def site():
    return AdminSite()


@pytest.fixture
def admin_client(client, db):
    admin = User.objects.create_superuser(
        "admin", "admin@example.com", "password123"
    )
    client.force_login(admin)
    return client


@pytest.fixture
def category():
    return Category.objects.create(name="Tech", slug="tech")


@pytest.fixture
def source():
    return NewsSource.objects.create(name="BBC", slug="bbc")


@pytest.fixture
def article(category, source):
    return Article.objects.create(
        title="Admin Test Article",
        content="Content for admin test",
        category=category,
        source=source,
        url="https://example.com/test-article",
        slug="admin-test-article"
    )


@pytest.mark.django_db
def test_article_admin_display_methods(site, article):
    admin = ArticleAdmin(Article, site)

    assert "Admin Test Article" in strip_tags(admin.title_link(article))

    # display_image might return a string or 'No Image'
    assert isinstance(admin.display_image(article), str)

    assert isinstance(admin.short_summary(article), str)


@pytest.mark.django_db
def test_news_source_admin_config(site):
    admin = NewsSourceAdmin(NewsSource, site)
    assert "slug" in admin.prepopulated_fields


@pytest.mark.django_db
def test_category_admin_icon_preview(category):
    admin = CategoryAdmin(Category, AdminSite())
    result = admin.icon_preview(category)
    assert result == "-" or '<img' in result


@pytest.mark.django_db
def test_custom_periodic_task_admin_changelist(admin_client):
    interval = IntervalSchedule.objects.create(
        every=1, period=IntervalSchedule.MINUTES
    )
    PeriodicTask.objects.create(
        name="Test Task",
        task="apps.news.tasks.fetch_news_articles",
        interval=interval,
        enabled=True,
    )
    url = reverse("admin:django_celery_beat_periodictask_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_custom_interval_schedule_admin_changelist(admin_client):
    IntervalSchedule.objects.create(
        every=10,
        period=IntervalSchedule.MINUTES
    )
    url = reverse("admin:django_celery_beat_intervalschedule_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200
    assert b"Fetch Intervals" in response.content


@pytest.mark.django_db
def test_run_now_view_triggers_task(admin_client):
    interval = IntervalSchedule.objects.create(
        every=1, period=IntervalSchedule.MINUTES
    )
    task = PeriodicTask.objects.create(
        name="Test Task",
        task="apps.news.tasks.fetch_news_articles",
        interval=interval,
        enabled=True,
    )
    url = reverse("admin:run_news_task_now", args=[task.pk])
    response = admin_client.post(url, follow=True)
    assert response.status_code == 200
    content = response.content.lower()
    success_triggered = b"success" in content or b"triggered" in content
    assert success_triggered
