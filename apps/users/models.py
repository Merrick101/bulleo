from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.apps import apps  # Lazy import

User = get_user_model()  # Dynamically load user model


# Category Model for News Preferences
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True, help_text="A brief description of the category")
    icon = models.ImageField(upload_to="images/category_icons/", blank=True, null=True, help_text="Optional icon for the category")
    order = models.PositiveIntegerField(default=0, help_text="Order for displaying categories")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a slug automatically from the name
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="static/images/profile_pics/",
        default="profile_pics/default.jpg",
        blank=True,
        null=True
    )
    preferred_categories = models.ManyToManyField(Category, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Comment Model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    article = models.ForeignKey("news.Article", on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")

    # Voting System (we rely on the many-to-many relationships)
    upvotes = models.ManyToManyField(User, related_name="upvoted_comments", blank=True)
    downvotes = models.ManyToManyField(User, related_name="downvoted_comments", blank=True)

    # Report field: marks a comment as reported/harmful.
    reported = models.BooleanField(default=False)

    # Deleted flag (optional but useful)
    deleted = models.BooleanField(default=False)

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
        # Mark the comment as deleted
        self.content = "[Deleted]"
        self.user = None
        self.deleted = True
        self.save()

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Comment by {username} on {self.article.title}"
