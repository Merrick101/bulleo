"""
Models for the News application.
This module defines the data models for news articles and sources,
including their relationships and fields.
Located at: apps/news/models.py
"""

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Model to represent a news source
class NewsSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=100, unique=True
    )
    slug = models.SlugField(
        max_length=100, unique=True, blank=True
    )
    description = models.TextField(
        blank=True, null=True, help_text="A brief description of the category"
    )
    icon = models.ImageField(
        upload_to="images/category_icons/", blank=True, null=True,
        help_text="Optional icon for the category"
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Order for displaying categories"
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField(db_index=True)
    summary = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(
        User, blank=True, related_name='liked_articles'
    )
    saves = models.ManyToManyField(
        User, blank=True, related_name='saved_articles'
    )

    # Link to article source and category
    source = models.ForeignKey(
        'news.NewsSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )

    category = models.ForeignKey(
        'news.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.title} ({self.published_at.strftime('%Y-%m-%d')})"

    def get_absolute_url(self):
        return reverse(
            "news:article_detail", kwargs={"article_id": self.id}
        )
