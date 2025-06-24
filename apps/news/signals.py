"""
Signal handlers for the News app.
This module contains signal handlers that automatically generate
unique slugs for news articles before they are saved to the database.
Located at: apps/news/signals.py
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Article, Category


@receiver(pre_save, sender=Article)
def generate_unique_slug(sender, instance, **kwargs):
    """
    Automatically generate a unique slug for new Article instances
    before saving.
    """
    if not instance.slug:
        base_slug = slugify(instance.title)
        slug = base_slug
        counter = 1
        while Article.objects.filter(
            slug=slug
        ).exclude(id=instance.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        instance.slug = slug


@receiver(pre_save, sender=Category)
def generate_category_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)
