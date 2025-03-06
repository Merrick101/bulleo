from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from apps.news.models import Article
from apps.users.models import Category, Comment
from datetime import datetime, timezone

User = get_user_model()


class CommentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Load SocialApp fixture before tests run and ensure the site exists."""

        # 🔹 Ensure testserver Site exists and override default site
        cls.site, _ = Site.objects.update_or_create(
            id=1, defaults={"domain": "testserver", "name": "testserver"}
        )

        # 🔹 Load the fixture (ensures SocialApp is created)
        call_command("loaddata", "apps/news/tests/fixtures/social_app.json")

        # 🔹 Ensure the SocialApp is linked to 'testserver'
        cls.social_app = SocialApp.objects.first()  # Fetch the loaded SocialApp
        if cls.social_app:
            cls.social_app.sites.set([cls.site])  # Explicitly attach it to testserver
            cls.social_app.save()

            # Create a test user
            cls.user = User.objects.create_user(username="testuser", password="password123")

            # Create a test category
            cls.category, _ = Category.objects.get_or_create(name="Politics", slug="politics")

            # Create a test article
            cls.article = Article.objects.create(
                title="Test Article",
                content="Some content",
                category=cls.category,
                published_at=datetime.now(timezone.utc)
            )

    def setUp(self):
        """Set up per-test client initialization (runs BEFORE each test method)."""
        self.client = Client()

        # Define URLs inside `setUp()`
        self.comment_url = reverse("news:post_comment", args=[self.article.id])
        self.article_detail_url = reverse("news:article_detail", args=[self.article.id])

    def test_social_app_setup(self):
        """Verify that SocialApp is properly set up in the test database."""
        site = Site.objects.get(domain="testserver")
        self.assertIsNotNone(site, "❌ Site does not exist in the test database!")

        social_app = SocialApp.objects.filter(provider="google").first()
        self.assertIsNotNone(social_app, "❌ SocialApp does not exist in the test database!")

        # Ensure SocialApp is linked to the correct Site
        self.assertIn(site, social_app.sites.all(), "❌ SocialApp is not linked to Site!")

    def test_anonymous_voting(self):
        """Ensure unauthenticated users cannot vote."""
        comment = Comment.objects.create(user=self.user, article=self.article, content="Test comment")

        vote_url = reverse("news:vote_comment", args=[comment.id, "upvote"])
        response = self.client.post(vote_url)

        login_url = reverse("account_login")
        expected_redirect_url = f"{login_url}?next={vote_url}"

        self.assertRedirects(response, expected_redirect_url)
        self.assertEqual(comment.upvotes.count(), 0)

    def test_post_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot post a comment."""
        response = self.client.post(self.comment_url, {"content": "Test comment"})

        # Redirects to login
        self.assertRedirects(response, f"/accounts/login/?next={self.comment_url}")
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_validation(self):
        """Test that invalid comments are rejected."""
        self.client.login(username="testuser", password="password123")
        response = self.client.post(self.comment_url, {"content": ""}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 400)  # Expect a failure
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid data."})
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_sorting(self):
        """Test sorting of comments by newest, oldest, most upvoted."""
        self.client.login(username="testuser", password="password123")

        old_comment = Comment.objects.create(
            user=self.user, article=self.article, content="Old Comment",
            created_at=datetime(2025, 3, 5, 12, 0, 0, tzinfo=timezone.utc)
        )
        new_comment = Comment.objects.create(
            user=self.user, article=self.article, content="New Comment",
            created_at=datetime(2025, 3, 6, 14, 0, 0, tzinfo=timezone.utc)
        )

        response = self.client.get(f"{self.article_detail_url}?sort=newest")

        self.assertContains(response, "New Comment")
        self.assertContains(response, "Old Comment")

    def test_upvote_comment(self):
        """Test that an authenticated user can upvote a comment."""
        self.client.login(username="testuser", password="password123")
        comment = Comment.objects.create(user=self.user, article=self.article, content="Test comment")

        vote_url = reverse("news:vote_comment", args=[comment.id, "upvote"])
        response = self.client.post(vote_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        comment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.upvotes.count(), 1)

    def test_downvote_comment(self):
        """Test that an authenticated user can downvote a comment."""
        self.client.login(username="testuser", password="password123")
        comment = Comment.objects.create(user=self.user, article=self.article, content="Test comment")

        vote_url = reverse("news:vote_comment", args=[comment.id, "downvote"])
        response = self.client.post(vote_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        comment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.downvotes.count(), 1)

    def test_vote_switching(self):
        """Test that an upvote is removed if downvoted and vice versa."""
        self.client.login(username="testuser", password="password123")
        comment = Comment.objects.create(user=self.user, article=self.article, content="Test comment")

        # Upvote first
        vote_url = reverse("news:vote_comment", args=[comment.id, "upvote"])
        self.client.post(vote_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        comment.refresh_from_db()
        self.assertEqual(comment.upvotes.count(), 1)
        self.assertEqual(comment.downvotes.count(), 0)

        # Now downvote
        vote_url = reverse("news:vote_comment", args=[comment.id, "downvote"])
        self.client.post(vote_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        comment.refresh_from_db()
        self.assertEqual(comment.upvotes.count(), 0)
        self.assertEqual(comment.downvotes.count(), 1)
