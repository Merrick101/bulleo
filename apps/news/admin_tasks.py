"""
Admin configuration for managing periodic tasks related to news fetching.
Located at: apps/news/admin_tasks.py
"""

from django.contrib import admin, messages
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django_celery_beat.admin import PeriodicTaskAdmin, IntervalScheduleAdmin
from celery import current_app

# Monkey-patch model names for clarity in the sidebar
PeriodicTask._meta.verbose_name = "News Fetch Task"
PeriodicTask._meta.verbose_name_plural = "News Fetch Tasks"

IntervalSchedule._meta.verbose_name = "Fetch Interval"
IntervalSchedule._meta.verbose_name_plural = "Fetch Intervals"

# Override the app title (sidebar group label in Jazzmin)
apps.get_app_config("django_celery_beat").verbose_name = _("News Sync")


class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    """
    Custom admin class for PeriodicTask to:
    - Add help text to the changelist view
    - Allow manual triggering of tasks via a custom action
    """
    actions = ["run_selected_tasks_now"]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "News Fetch Tasks"
        extra_context["help_text"] = (
            "This section controls how news articles are"
            "automatically fetched."
            "Use the Fetch Intervals to adjust timing,"
            "or click into a task to modify it."
        )
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Run selected News Fetch Tasks now")
    def run_selected_tasks_now(self, request, queryset):
        """
        Trigger selected tasks immediately via Celery.
        """
        run_count = 0
        for task in queryset:
            try:
                current_app.send_task(task.task)
                run_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to run task '{task.name}': {e}",
                    level=messages.ERROR,
                )
        if run_count:
            self.message_user(
                request,
                _(f"{run_count} task(s) triggered successfully."),
                level=messages.SUCCESS,
            )


# Unregister original admin classes to avoid conflicts
for model in [PeriodicTask, IntervalSchedule]:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Re-register with updated admin classes
admin.site.register(PeriodicTask, CustomPeriodicTaskAdmin)
admin.site.register(IntervalSchedule, IntervalScheduleAdmin)
