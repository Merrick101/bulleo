from django.db import models
from django.utils.text import slugify
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
    slug = models.SlugField(max_length=255, unique=True)

    # Link to article source and category
    source = models.ForeignKey(
        'news.NewsSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )

    category = models.ForeignKey(
        'users.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.title} ({self.published_at.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        # Ensure that slug is generated from title if it's not already set
        if not self.slug:
            self.slug = slugify(self.title)

        # Ensure uniqueness of the slug
        original_slug = self.slug
        counter = 1
        while Article.objects.filter(slug=self.slug).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1

        # Save the object with the unique slug
        super().save(*args, **kwargs)
