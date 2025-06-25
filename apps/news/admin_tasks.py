"""
Admin configuration for managing periodic tasks related to news fetching.
Located at: apps/news/admin_tasks.py
"""

from django.contrib import admin
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django_celery_beat.admin import PeriodicTaskAdmin, IntervalScheduleAdmin

# Monkey-patch model names for clarity in the sidebar
PeriodicTask._meta.verbose_name = "News Fetch Task"
PeriodicTask._meta.verbose_name_plural = "News Fetch Tasks"

IntervalSchedule._meta.verbose_name = "Fetch Interval"
IntervalSchedule._meta.verbose_name_plural = "Fetch Intervals"

# Override the app title (sidebar group label in Jazzmin)
apps.get_app_config("django_celery_beat").verbose_name = _("News Sync")


# Custom admin class to inject context help into changelist
class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = "News Fetch Tasks"
        extra_context['help_text'] = (
            "This section controls how news articles"
            "are automatically fetched. "
            "Use the Fetch Intervals to adjust timing,"
            "or click into a task to modify it."
        )
        return super().changelist_view(request, extra_context=extra_context)


# Unregister original admin classes to avoid conflicts
for model in [PeriodicTask, IntervalSchedule]:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Re-register with custom admin class (only for PeriodicTask)
admin.site.register(PeriodicTask, CustomPeriodicTaskAdmin)
admin.site.register(IntervalSchedule, IntervalScheduleAdmin)
