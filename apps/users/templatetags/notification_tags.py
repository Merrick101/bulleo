"""
Custom template tags for rendering recent user notifications.
Located in apps/users/templatetags/notification_tags.py
"""

from django import template

register = template.Library()


@register.inclusion_tag("partials/notifications_preview.html")
def recent_notifications(user, limit=3):
    if user.is_authenticated:
        notifications = user.notifications.filter(
            read=False
        ).order_by('-created_at')[:limit]
        return {"notifications": notifications}
    return {"notifications": []}
