from django.contrib import admin
from django.utils.html import format_html
from .models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title_link', 'published_at', 'source', 'category', 'display_image')
    list_filter = ('published_at', 'source', 'category')
    search_fields = ('title', 'content', 'summary')
    date_hierarchy = 'published_at'

    def title_link(self, obj):
        try:
            url = obj.get_absolute_url()
        except Exception:
            # Fallback if URL cannot be reversed
            url = "#"
        return format_html('<a href="{}">{}</a>', url, obj.title)
    title_link.short_description = "Title"

    def display_image(self, obj):
        if obj.image_url:
            try:
                url = obj.get_absolute_url()
            except Exception:
                url = "#"
            return format_html(
                '<a href="{}"><img src="{}" width="100" height="60" /></a>',
                url, obj.image_url
            )
        return "No Image"
    display_image.short_description = "Article Image"


admin.site.register(Article, ArticleAdmin)
