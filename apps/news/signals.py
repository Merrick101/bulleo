from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
from apps.users.models import Profile, Notification, Comment
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def notify_new_article(sender, instance, created, **kwargs):
    if created and instance.category:
        for profile in Profile.objects.filter(preferred_categories=instance.category):
            message = f"New article in {instance.category.name}: '{instance.title}'"
            Notification.objects.create(
                user=profile.user,
                message=message,
                link=instance.get_absolute_url()
            )


@receiver(post_save, sender=Comment)
def notify_comment_reply(sender, instance, created, **kwargs):
    if created and instance.parent:
        original_snippet = instance.parent.content[:50]  # first 50 characters
        message = f"{instance.user.username} replied to your comment: '{original_snippet}...'"
        Notification.objects.create(
            user=instance.parent.user,
            message=message,
            link=instance.article.get_absolute_url()
        )
