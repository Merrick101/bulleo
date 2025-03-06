from django.db import models
from apps.users.models import Category

# Create your models here.


# Model to represent a news source
class NewsSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField(db_index=True)
    summary = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(unique=True)

    # Link to article source and category
    source = models.ForeignKey(
        NewsSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.title} ({self.published_at.strftime('%Y-%m-%d')})"
