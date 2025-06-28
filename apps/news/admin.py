"""
Admin configuration for the News app.
Located at: apps/news/admin.py
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import Article, NewsSource, Category


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title_link', 'published_at', 'source', 'category',
        'short_summary', 'views', 'display_image'
    )
    list_filter = (
        'published_at', 'source', 'category'
    )
    search_fields = (
        'title', 'content', 'summary', 'url'
    )
    date_hierarchy = 'published_at'
    readonly_fields = ('slug', 'published_at', 'views')
    ordering = ('-published_at',)

    def title_link(self, obj):
        try:
            url = obj.get_absolute_url()
        except Exception:
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

    def short_summary(self, obj):
        if obj.summary:
            return (
                obj.summary[:75] + '...'
            ) if len(obj.summary) > 75 else obj.summary
        return "-"
    short_summary.short_description = "Summary"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _like_count=Count('likes'),
            _save_count=Count('saves'),
        )

    def like_count(self, obj):
        return getattr(obj, '_like_count', 0)
    like_count.admin_order_field = '_like_count'
    like_count.short_description = "Likes"

    def save_count(self, obj):
        return getattr(obj, '_save_count', 0)
    save_count.admin_order_field = '_save_count'
    save_count.short_description = "Saves"


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'website')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'icon_preview')
    list_editable = ('order',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" width="40" height="40" />', obj.icon.url
            )
        return "-"
    icon_preview.short_description = "Icon Preview"

import apps.news.admin_tasks  # NOQA
