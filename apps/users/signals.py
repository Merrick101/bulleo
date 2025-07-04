"""
Signal handlers for user-related events like
profile creation and notifications.
Located at: apps/users/signals.py
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Notification, Comment
from apps.news.models import Article
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile for every newly registered User.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User, dispatch_uid="save_user_profile")
def save_profile(sender, instance, **kwargs):
    """
    Save the user's profile after updates to the User instance.
    """
    if hasattr(instance, 'profile') and instance.profile:
        instance.profile.save()


@receiver(post_save, sender=Article)
def notify_new_article(sender, instance, created, **kwargs):
    """
    Notify users when a new article is posted in a category they follow.
    """
    if created and instance.category:
        for profile in Profile.objects.filter(
            preferred_categories=instance.category
        ):
            if profile.notifications_enabled:
                message = (
                    f"New article in {instance.category.name}: "
                    f"'{instance.title}'"
                )
                Notification.objects.create(
                    user=profile.user,
                    message=message,
                    link=instance.get_absolute_url()
                )


@receiver(post_save, sender=Comment)
def notify_comment_reply(sender, instance, created, **kwargs):
    """
    Notify the parent commenter when their comment receives a reply.
    """
    if created and instance.parent and instance.parent.user:
        parent_user = instance.parent.user
        if hasattr(
            parent_user, 'profile'
        ) and parent_user.profile.notifications_enabled:
            original_snippet = instance.parent.content[:50]
            message = (
                f"{instance.user.username} replied to your comment: "
                f"'{original_snippet}...'"
            )
            Notification.objects.create(
                user=parent_user,
                message=message,
                link=instance.article.get_absolute_url()
            )
