from django.contrib import admin
from .models import Profile, Comment, Notification


# Register Profile with more fields in list_display
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'created_at', 'profile_picture')  # Display bio and profile picture
    search_fields = ('user__username', 'bio')  # Search by username and bio
    list_filter = ('created_at',)  # Filter by creation date
    ordering = ('-created_at',)  # Order by most recent profile
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
            return queryset.filter(parent__isnull=False)  # Replies have a parent
        if self.value() == 'False':
            return queryset.filter(parent__isnull=True)  # Parent comments have no parent
        return queryset


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'content', 'created_at', 'parent', 'upvote_count', 'downvote_count')  # Show vote counts
    search_fields = ('content', 'user__username', 'article__title')  # Search by content, username, and article title
    list_filter = ('created_at', IsReplyFilter)  # Add the custom filter here
    ordering = ('-created_at',)  # Order comments by most recent first
    list_per_page = 25  # Display 25 comments per page in the admin panel

    def upvote_count(self, obj):
        return obj.upvotes.count()

    def downvote_count(self, obj):
        return obj.downvotes.count()

    upvote_count.admin_order_field = 'upvotes'  # Make upvote count sortable
    downvote_count.admin_order_field = 'downvotes'  # Make downvote count sortable

    def parent(self, obj):
        # Display the content of the parent comment if it's a reply
        if obj.parent:
            return obj.parent.content[:50]  # Display the first 50 characters of the parent content
        return None
    parent.admin_order_field = 'parent'  # Make parent sortable


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('message', 'user__username')
    ordering = ('-created_at',)
