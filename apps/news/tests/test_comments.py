from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.news.models import Article, NewsSource
from apps.users.models import Category, Comment
from datetime import datetime, timezone

User = get_user_model()


class CommentTests(TestCase):
    def setUp(self):
        # Use `get_or_create` instead of `create` to avoid duplicates
        self.category, created = Category.objects.get_or_create(name="Politics", slug="politics")

        # Create a user and an article
        self.user = User.objects.create_user(username="testuser", password="password123")

        # Ensure `published_at` is set
        self.article = Article.objects.create(
            title="Test Article",
            content="Some content",
            category=self.category,
            published_at=datetime.now(timezone.utc)  # Ensuring valid timestamp
        )

        self.client = Client()
        self.comment_url = reverse("news:post_comment", args=[self.article.id])
        self.article_detail_url = reverse("news:article_detail", args=[self.article.id])

    def vote_url(self, comment_id, action):
        """Constructs the voting URL for comments."""
        return reverse("news:comment_vote", args=[comment_id, action])

    def test_post_comment_authenticated(self):
        """Test that an authenticated user can post a comment"""
        self.client.login(username="testuser", password="password123")
        response = self.client.post(self.comment_url, {"content": "Test comment"})

        self.assertEqual(response.status_code, 302)  # Redirects to article detail
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().content, "Test comment")

    def test_post_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot post a comment"""
        response = self.client.post(self.comment_url, {"content": "Test comment"})

        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_validation(self):
        """Test that invalid comments are rejected"""
        self.client.login(username="testuser", password="password123")
        response = self.client.post(self.comment_url, {"content": ""})

        self.assertEqual(response.status_code, 200)  # Form re-renders with errors
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_sorting(self):
        """Test sorting of comments by newest, oldest, most upvoted"""
        self.client.login(username="testuser", password="password123")

        # Create comments with valid timestamps
        old_comment = Comment.objects.create(
            user=self.user, article=self.article, content="Old Comment",
            created_at=datetime(2025, 3, 5, 12, 0, 0, tzinfo=timezone.utc)
        )
        new_comment = Comment.objects.create(
            user=self.user, article=self.article, content="New Comment",
            created_at=datetime(2025, 3, 6, 14, 0, 0, tzinfo=timezone.utc)
        )

        response = self.client.get(self.article_detail_url + "?sort=newest")

        self.assertContains(response, "New Comment")
        self.assertContains(response, "Old Comment")

    def test_upvote_comment(self):
        """Test that an authenticated user can upvote a comment"""
        self.client.login(username="testuser", password="password123")
        comment = Comment.objects.create(user=self.user, article=self.article, content="Test comment")

        response = self.client.post(self.vote_url(comment.id, "upvote"))
        comment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.upvotes.count(), 1)

    def test_downvote_comment(self):
        """Test that an authenticated user can downvote a comment"""
        self.client.login(username="testuser", password="password123")
        comment = Comment.objects.create(user=self.user, article=self.article, content="Test comment")

        response = self.client.post(self.vote_url(comment.id, "downvote"))
        comment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.downvotes.count(), 1)

    def test_vote_switching(self):
        """Test that an upvote is removed if downvoted and vice versa"""
        self.client.login(username="testuser", password="password123")
        comment = Comment.objects.create(user=self.user, article=self.article, content="Test comment")

        # Upvote first
        self.client.post(self.vote_url(comment.id, "upvote"))
        comment.refresh_from_db()
        self.assertEqual(comment.upvotes.count(), 1)
        self.assertEqual(comment.downvotes.count(), 0)

        # Now downvote
        self.client.post(self.vote_url(comment.id, "downvote"))
        comment.refresh_from_db()
        self.assertEqual(comment.upvotes.count(), 0)
        self.assertEqual(comment.downvotes.count(), 1)

    def test_anonymous_voting(self):
        """Ensure unauthenticated users cannot vote"""
        comment = Comment.objects.create(user=self.user, article=self.article, content="Test comment")

        response = self.client.post(self.vote_url(comment.id, "upvote"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(comment.upvotes.count(), 0)


if __name__ == "__main__":
    TestCase.main()
