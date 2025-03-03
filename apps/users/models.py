from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.text import slugify

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
