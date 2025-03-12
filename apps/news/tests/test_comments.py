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
        """Load SocialApp fixture and create test data for comments."""
        # Ensure the test server Site exists
        cls.site, _ = Site.objects.update_or_create(
            id=1, defaults={"domain": "testserver", "name": "testserver"}
        )

        # Load SocialApp fixture
        call_command("loaddata", "apps/news/tests/fixtures/social_app.json")

        # Link SocialApp to the test server
        cls.social_app = SocialApp.objects.first()
        if cls.social_app:
            cls.social_app.sites.set([cls.site])
            cls.social_app.save()

        # Create users
        cls.user = User.objects.create_user(username="testuser", password="password123")
        cls.other_user = User.objects.create_user(username="otheruser", password="password123")

        # Create a category (from the users app)
        cls.category, _ = Category.objects.get_or_create(name="Politics", slug="politics")

        # Create an article (from the news app)
        cls.article = Article.objects.create(
            title="Test Article",
            content="Some content",
            category=cls.category,
            published_at=datetime.now(timezone.utc)
        )

        # Create a comment (from the users app)
        cls.comment = Comment.objects.create(
            user=cls.user,
            article=cls.article,
            content="Original Comment",
            created_at=datetime.now(timezone.utc)
        )

    def setUp(self):
        """Initialize the test client and URLs for each test."""
        self.client = Client()
        self.comment_url = reverse("news:post_comment", args=[self.article.id])
        self.comment_edit_url = reverse("news:edit_comment", args=[self.comment.id])
        self.comment_delete_url = reverse("news:delete_comment", args=[self.comment.id])

    def test_edit_comment_authenticated(self):
        """Test that the comment owner can edit their comment."""
        self.client.login(username="testuser", password="password123")

        response = self.client.post(
            self.comment_edit_url,
            {"content": "Edited Comment"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.comment.content, "Edited Comment")

        json_response = response.json()
        self.assertTrue(json_response.get("success"))
        self.assertEqual(json_response.get("comment_id"), self.comment.id)
        self.assertEqual(json_response.get("updated_content"), "Edited Comment")
        expected_date = self.comment.created_at.strftime("%b %d, %Y %I:%M %p")
        self.assertEqual(json_response.get("updated_at"), expected_date)

    def test_edit_comment_unauthorized(self):
        """Test that a user cannot edit someone else's comment."""
        self.client.login(username="otheruser", password="password123")

        response = self.client.post(
            self.comment_edit_url,
            {"content": "Unauthorized Edit"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(self.comment.content, "Unauthorized Edit")

    def test_edit_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot edit a comment."""
        response = self.client.post(
            self.comment_edit_url,
            {"content": "Anonymous Edit"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        login_url = reverse("account_login")
        expected_redirect_url = f"{login_url}?next={self.comment_edit_url}"
        self.assertRedirects(response, expected_redirect_url)

        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.content, "Anonymous Edit")

    def test_edit_comment_invalid_content(self):
        """Test that an empty comment edit is rejected."""
        self.client.login(username="testuser", password="password123")

        response = self.client.post(
            self.comment_edit_url,
            {"content": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {"success": False, "error": "Comment cannot be empty."}
        )

    def test_delete_comment_authenticated(self):
        """Test that the comment owner can delete (soft-delete) their comment."""
        self.client.login(username="testuser", password="password123")

        response = self.client.post(
            self.comment_delete_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertTrue(json_response.get("success"))
        self.assertEqual(json_response.get("comment_id"), self.comment.id)
        # Expect the JSON to include additional keys from the deletion view:
        self.assertTrue(json_response.get("deleted"))
        self.assertIn("comment_count", json_response)

        # Instead of verifying that the comment is removed, we expect a soft deletion:
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.deleted)
        # Optionally, also check that the comment content has been replaced:
        self.assertEqual(self.comment.content, "[Deleted]")

    def test_delete_comment_unauthorized(self):
        """Test that a user cannot delete someone else's comment."""
        self.client.login(username="otheruser", password="password123")

        response = self.client.post(
            self.comment_delete_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a comment."""
        response = self.client.post(
            self.comment_delete_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        login_url = reverse("account_login")
        expected_redirect_url = f"{login_url}?next={self.comment_delete_url}"
        self.assertRedirects(response, expected_redirect_url)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
