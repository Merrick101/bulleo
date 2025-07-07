import pytest
from django.utils.text import slugify
from apps.news.models import Article, Category, NewsSource


@pytest.mark.django_db
def test_article_slug_is_auto_generated():
    source = NewsSource.objects.create(
        name="Signal Source", slug="signal-source"
    )
    article = Article.objects.create(
        title="Signal Testing Article",
        url="https://example.com/signal-article",
        content="Test content",
        source=source,
    )

    expected_slug = slugify(article.title)
    assert article.slug == expected_slug


@pytest.mark.django_db
def test_article_slug_uniqueness():
    source = NewsSource.objects.create(name="Source", slug="source")
    title = "Same Title"
    url1 = "https://example.com/article1"
    url2 = "https://example.com/article2"

    article1 = Article.objects.create(
        title=title, url=url1, content="One", source=source
    )
    article2 = Article.objects.create(
        title=title, url=url2, content="Two", source=source
    )

    assert article1.slug == slugify(title)
    assert article2.slug.startswith(slugify(title))
    assert article1.slug != article2.slug


@pytest.mark.django_db
def test_category_slug_is_generated():
    category = Category.objects.create(name="Tech & Gadgets")
    expected_slug = slugify(category.name)
    assert category.slug == expected_slug
