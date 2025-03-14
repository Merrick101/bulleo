from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
from apps.users.models import Profile, Notification, Comment
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def notify_new_article(sender, instance, created, **kwargs):
    if created:
        logger.info("Article created: %s", instance.title)
        # Get the article's category
        category = instance.category
        if category:
            # Find all profiles that prefer this category
            profiles = Profile.objects.filter(preferred_categories=category)
            for profile in profiles:
                Notification.objects.create(
                    user=profile.user,
                    message=f"New article in {category.name}: {instance.title}",
                    link=instance.get_absolute_url()
                )


@receiver(post_save, sender=Comment)
def notify_comment_reply(sender, instance, created, **kwargs):
    if created and instance.parent:
        logger.info(
            "Creating notification for comment reply: Parent ID %s, Reply by %s on Article ID %s",
            instance.parent.id,
            instance.user.username if instance.user else "Anonymous",
            instance.article.id
        )
        Notification.objects.create(
            user=instance.parent.user,
            message=f"{instance.user.username} replied to your comment.",
            link=instance.article.get_absolute_url()
        )
