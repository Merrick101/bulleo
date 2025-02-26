from django.db import models

# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    # Store external image links
    image_url = models.URLField(max_length=500, blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
