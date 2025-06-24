"""
Models for the Users app, including user profiles,
categories for news preferences, comments, and notifications.
Located at: apps/users/models.py
"""

from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

User = get_user_model()  # Dynamically load user model


# User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(
        blank=True, null=True
    )
    profile_picture = CloudinaryField(
        "image", default="placeholder.jpg"
    )  # Cloudinary field
    preferred_categories = models.ManyToManyField(
        "news.Category", blank=True
    )
    notifications_enabled = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Comment Model
class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    article = models.ForeignKey(
        "news.Article", on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="replies"
    )

    # Voting System (we rely on the many-to-many relationships)
    upvotes = models.ManyToManyField(
        User, related_name="upvoted_comments", blank=True
    )
    downvotes = models.ManyToManyField(
        User, related_name="downvoted_comments", blank=True
    )

    # Report field: marks a comment as reported/harmful.
    reported = models.BooleanField(
        default=False
    )

    # Deleted flag (optional but useful)
    deleted = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ['created_at']

    def get_replies(self):
        return self.replies.order_by("created_at")

    def upvote(self, user):
        if not self.has_upvoted(user):
            self.upvotes.add(user)
            self.downvotes.remove(user)
            self.save()

    def downvote(self, user):
        if not self.has_downvoted(user):
            self.downvotes.add(user)
            self.upvotes.remove(user)
            self.save()

    def has_upvoted(self, user):
        return self.upvotes.filter(id=user.id).exists()

    def has_downvoted(self, user):
        return self.downvotes.filter(id=user.id).exists()

    def is_reply(self):
        return self.parent is not None

    def delete(self, *args, **kwargs):
        # Clear M2M relationships
        self.upvotes.clear()
        self.downvotes.clear()

        # Soft delete (if preferred)
        self.content = "[Deleted]"
        self.user = None
        self.deleted = True
        self.save()

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Comment by {username} on {self.article.title}"


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    message = models.TextField()
    link = models.URLField(
        blank=True, null=True
    )  # Optional link to the relevant content
    read = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}"
