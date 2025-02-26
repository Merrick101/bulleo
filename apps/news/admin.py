from django.contrib import admin
from django.utils.html import format_html
from .models import Article


# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'display_image')

    def display_image(self, obj):
        if obj.image_url:
            return format_html(f'<img src="{obj.image_url}" width="100" height="60" />')
        return "No Image"

    display_image.short_description = "Article Image"


admin.site.register(Article, ArticleAdmin)
