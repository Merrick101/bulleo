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

        # Ensure testserver Site exists
        cls.site, _ = Site.objects.update_or_create(
            id=1, defaults={"domain": "testserver", "name": "testserver"}
        )

        # Load SocialApp fixture
        call_command("loaddata", "apps/news/tests/fixtures/social_app.json")

        # Ensure the SocialApp is linked to 'testserver'
        cls.social_app = SocialApp.objects.first()
        if cls.social_app:
            cls.social_app.sites.set([cls.site])
            cls.social_app.save()

        # Create users
        cls.user = User.objects.create_user(username="testuser", password="password123")
        cls.other_user = User.objects.create_user(username="otheruser", password="password123")

        # Create category
        cls.category, _ = Category.objects.get_or_create(name="Politics", slug="politics")

        # Create article
        cls.article = Article.objects.create(
            title="Test Article",
            content="Some content",
            category=cls.category,
            published_at=datetime.now(timezone.utc)
        )

        # Create comment
        cls.comment = Comment.objects.create(
            user=cls.user,
            article=cls.article,
            content="Original Comment",
            created_at=datetime.now(timezone.utc)
        )

    def setUp(self):
        """Set up per-test client initialization (runs BEFORE each test method)."""
        self.client = Client()
        self.comment_url = reverse("news:post_comment", args=[self.article.id])
        self.comment_edit_url = reverse("news:edit_comment", args=[self.comment.id])
        self.comment_delete_url = reverse("news:delete_comment", args=[self.comment.id])

    def test_edit_comment_authenticated(self):
        """Test that the comment owner can edit their comment."""
        self.client.login(username="testuser", password="password123")

        response = self.client.post(self.comment_edit_url, {
            "content": "Edited Comment"
        }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.comment.content, "Edited Comment")
        self.assertJSONEqual(response.content, {
            "success": True,
            "comment_id": self.comment.id,
            "updated_content": "Edited Comment",
            "updated_at": self.comment.created_at.strftime("%b %d, %Y %I:%M %p"),
        })

    def test_edit_comment_unauthorized(self):
        """Test that a user cannot edit someone else's comment."""
        self.client.login(username="otheruser", password="password123")

        response = self.client.post(self.comment_edit_url, {
            "content": "Unauthorized Edit"
        }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 404)  # Should return Not Found
        self.assertNotEqual(self.comment.content, "Unauthorized Edit")

    def test_edit_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot edit a comment."""
        response = self.client.post(self.comment_edit_url, {
            "content": "Anonymous Edit"
        }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        login_url = reverse("account_login")
        expected_redirect_url = f"{login_url}?next={self.comment_edit_url}"

        self.assertRedirects(response, expected_redirect_url)
        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.content, "Anonymous Edit")

    def test_edit_comment_invalid_content(self):
        """Test that an empty comment edit is rejected."""
        self.client.login(username="testuser", password="password123")

        response = self.client.post(self.comment_edit_url, {
            "content": ""
        }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            "success": False,
            "error": "Comment cannot be empty."
        })

    def test_delete_comment_authenticated(self):
        """Test that the comment owner can delete their comment."""
        self.client.login(username="testuser", password="password123")

        response = self.client.post(self.comment_delete_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": True,
            "comment_id": self.comment.id,
        })
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthorized(self):
        """Test that a user cannot delete someone else's comment."""
        self.client.login(username="otheruser", password="password123")

        response = self.client.post(self.comment_delete_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 404)  # Should return Not Found
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a comment."""
        response = self.client.post(self.comment_delete_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        login_url = reverse("account_login")
        expected_redirect_url = f"{login_url}?next={self.comment_delete_url}"

        self.assertRedirects(response, expected_redirect_url)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
