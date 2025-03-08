from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Explicitly create the profile only when a new user is created
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User, dispatch_uid="save_user_profile")
def save_profile(sender, instance, **kwargs):
    # Only save profile if there are changes to save
    if hasattr(instance, 'profile') and instance.profile:
        instance.profile.save()
