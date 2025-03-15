from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import datetime
from apps.news.models import Article, NewsSource
from apps.users.models import Category


class ArticleSearchTests(TestCase):
    def setUp(self):
        # Use get_or_create to avoid duplicates
        self.business_category, _ = Category.objects.get_or_create(name="Business", slug="business")
        self.sports_category, _ = Category.objects.get_or_create(name="Sports", slug="sports")

        # Create a news source (assume NewsSource has a slug field)
        self.source = NewsSource.objects.create(name="TestSource", slug="testsource")

        # Create some articles:
        # Article 1: Business article
        self.article1 = Article.objects.create(
            title="Business News Today",
            content="Some content about business.",
            summary="Summary business article.",
            url="http://example.com/business1",
            published_at=timezone.now() - datetime.timedelta(days=1),
            source=self.source,
            category=self.business_category
        )

        # Article 2: Sports article
        self.article2 = Article.objects.create(
            title="Sports Update",
            content="Latest sports content.",
            summary="Summary sports article.",
            url="http://example.com/sports1",
            published_at=timezone.now() - datetime.timedelta(days=2),
            source=self.source,
            category=self.sports_category
        )

        # Article 3: Business article with keyword "finance"
        self.article3 = Article.objects.create(
            title="Finance and Business",
            content="Finance is an important aspect of business.",
            summary="Summary finance article.",
            url="http://example.com/business2",
            published_at=timezone.now() - datetime.timedelta(days=3),
            source=self.source,
            category=self.business_category
        )

    def test_search_by_query(self):
        """
        Verify that a search query filters articles by title or content.
        """
        url = reverse('news:search_results')
        response = self.client.get(url, {'q': 'finance'})
        self.assertEqual(response.status_code, 200)
        articles = response.context['articles']
        # Only article3 contains 'finance'
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].id, self.article3.id)

    def test_filter_by_category(self):
        """
        Verify that filtering by category returns only articles in that category.
        """
        url = reverse('news:search_results')
        response = self.client.get(url, {'category': 'business'})
        self.assertEqual(response.status_code, 200)
        articles = response.context['articles']
        # Expect articles 1 and 3 in the 'business' category
        self.assertEqual(len(articles), 2)
        for article in articles:
            self.assertEqual(article.category.slug, 'business')

    def test_filter_by_source(self):
        """
        Verify that filtering by source returns articles from that source.
        """
        url = reverse('news:search_results')
        response = self.client.get(url, {'source': 'testsource'})
        self.assertEqual(response.status_code, 200)
        articles = response.context['articles']
        # All three articles are from TestSource
        self.assertEqual(len(articles), 3)

    def test_sort_most_recent(self):
        """
        Verify that sorting by 'most_recent' orders articles by published_at descending.
        """
        url = reverse('news:search_results')
        response = self.client.get(url, {'sort': 'most_recent'})
        self.assertEqual(response.status_code, 200)
        articles = list(response.context['articles'])
        # Ensure articles are in descending order of published_at
        for i in range(len(articles) - 1):
            self.assertGreaterEqual(articles[i].published_at, articles[i+1].published_at)

    def test_sort_oldest(self):
        """
        Verify that sorting by 'oldest' orders articles by published_at ascending.
        """
        url = reverse('news:search_results')
        response = self.client.get(url, {'sort': 'oldest'})
        self.assertEqual(response.status_code, 200)
        articles = list(response.context['articles'])
        for i in range(len(articles) - 1):
            self.assertLessEqual(articles[i].published_at, articles[i+1].published_at)
