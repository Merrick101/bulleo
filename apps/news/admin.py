from django.contrib import admin
from django.utils.html import format_html
from .models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'source', 'category', 'display_image')
    list_filter = ('published_at', 'source', 'category')  # Filters in the sidebar
    search_fields = ('title', 'content', 'summary')        # Search capability
    date_hierarchy = 'published_at'                        # Quick date navigation

    def display_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="100" height="60" />', obj.image_url)
        return "No Image"

    display_image.short_description = "Article Image"


admin.site.register(Article, ArticleAdmin)
