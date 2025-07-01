"""
Admin configuration for the Users app.
Located at: apps/users/admin.py
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Comment, Notification, ContactMessage


# Register Profile with more fields in list_display
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'bio', 'created_at'
    )  # Display bio and profile picture
    search_fields = (
        'user__username', 'bio'
    )  # Search by username and bio
    list_filter = (
        'created_at',
    )  # Filter by creation date
    ordering = (
        '-created_at',
    )  # Order by most recent profile
    list_per_page = 25  # Display 25 profiles per page


# Custom filter for determining if a comment is a reply or not
class IsReplyFilter(admin.SimpleListFilter):
    title = 'Is Reply'  # The label for the filter
    parameter_name = 'is_reply'

    def lookups(self, request, model_admin):
        # Options available in the filter
        return (
            ('True', 'Is a reply'),
            ('False', 'Is a parent comment'),
        )

    def queryset(self, request, queryset):
        # Filter logic based on the selected value in the filter dropdown
        if self.value() == 'True':
            return queryset.filter(
                parent__isnull=False
            )  # Replies have a parent
        if self.value() == 'False':
            return queryset.filter(
                parent__isnull=True
            )  # Parent comments have no parent
        return queryset


class DeletedFilter(admin.SimpleListFilter):
    title = 'Deleted Status'
    parameter_name = 'deleted'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Deleted'),
            ('no', 'Visible'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(deleted=True)
        if self.value() == 'no':
            return queryset.filter(deleted=False)
        return queryset


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'article', 'short_content', 'created_at',
        'parent_link', 'upvote_count', 'downvote_count',
        'is_reported', 'is_deleted'
    )
    search_fields = (
        'content', 'user__username', 'article__title'
    )
    list_filter = (
        'created_at', 'reported', DeletedFilter, IsReplyFilter
    )
    ordering = (
        '-created_at',
    )
    list_per_page = 25
    list_select_related = (
        'user', 'article', 'parent'
    )

    def is_reported(self, obj):
        return obj.reported
    is_reported.boolean = True
    is_reported.short_description = "Reported"

    def is_deleted(self, obj):
        return obj.deleted
    is_deleted.boolean = True
    is_deleted.short_description = "Deleted"

    def short_content(self, obj):
        return obj.content[:50] + (
            "..." if len(obj.content) > 50 else ""
        )
    short_content.short_description = "Content"

    def parent_link(self, obj):
        if obj.parent:
            return format_html(
                '<a href="{}">{}</a>', obj.parent.get_absolute_url(),
                obj.parent.content[:50]
            )
        return "N/A"
    parent_link.short_description = "Parent Comment"

    def upvote_count(self, obj):
        return obj.upvotes.count()
    upvote_count.admin_order_field = 'upvotes'

    def downvote_count(self, obj):
        return obj.downvotes.count()
    downvote_count.admin_order_field = 'downvotes'

    actions = ['mark_as_reviewed']

    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(reported=False)
        self.message_user(request, f"{updated} comments marked as reviewed.")
    mark_as_reviewed.short_description = "Mark selected comments as reviewed"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('message', 'user__username')
    ordering = ('-created_at',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'replied')
    list_filter = ('replied', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
