from django.contrib import admin
from .models import Profile, Comment

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')


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
    list_display = ('user', 'article', 'content', 'created_at', 'parent')
    search_fields = ('content', 'user__username', 'article__title')  # Search by content, username, and article title
    list_filter = ('created_at', IsReplyFilter)  # Add the custom filter here
    ordering = ('-created_at',)  # Order comments by most recent first
    list_per_page = 25  # Display 25 comments per page in the admin panel
