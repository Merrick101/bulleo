from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


# Category Model for News Preferences
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="static/images/profile_pics/",
        default="profile_pics/default.jpg",
        blank=True,
        null=True
    )
    # Use ManyToMany for better filtering
    news_preferences = models.ManyToManyField(Category, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Ensure email is provided before saving user
@receiver(pre_save, sender=User)
def validate_user_email(sender, instance, **kwargs):
    if not instance.email:
        raise ValidationError("An email address is required to create an account.")


# Automatically create and save Profile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
