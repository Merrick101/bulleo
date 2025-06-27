"""
Admin configuration for managing periodic tasks related to news fetching.
Located at: apps/news/admin_tasks.py
"""

from django.contrib import admin, messages
from django.apps import apps
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html  # NOQA
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django_celery_beat.admin import (
    PeriodicTaskAdmin,
    IntervalScheduleAdmin
)
from celery import current_app


# Rename models in sidebar
PeriodicTask._meta.verbose_name = "News Fetch Task"
PeriodicTask._meta.verbose_name_plural = "News Fetch Tasks"
IntervalSchedule._meta.verbose_name = "Fetch Interval"
IntervalSchedule._meta.verbose_name_plural = "Fetch Intervals"

# Rename app section in sidebar
apps.get_app_config("django_celery_beat").verbose_name = _("News Sync")


class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    """
    Custom admin for periodic tasks with:
    - Inline changelist help text
    - Manual task triggering via action
    - Description preview in list_display
    """
    actions = ["run_selected_tasks_now"]
    change_form_template = "admin/news/fetch_task_change_form.html"
    list_display = (
        "name", "description_snippet", "interval", "enabled",
        "start_time", "last_run_at", "one_off"
    )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "News Fetch Tasks"
        extra_context["help_text"] = (
            "<div style='padding:10px; background:#f4f9ff; border-left: 5px "
            "solid #007acc;'>"
            "<strong>Instructions:</strong><br>"
            "These are scheduled tasks that automatically fetch articles "
            "based on their configured interval. Use the action menu to "
            "trigger a fetch manually."
            "</div>"
        )
        return super().changelist_view(request, extra_context=extra_context)

    def description_snippet(self, obj):
        if obj.description:
            return (
                obj.description[:60] + "..."
                ) if len(obj.description) > 60 \
                else obj.description
        return "-"
    description_snippet.short_description = "Description"

    @admin.action(description="Run selected News Fetch Tasks now")
    def run_selected_tasks_now(self, request, queryset):
        run_count = 0
        for task in queryset:
            try:
                current_app.send_task(task.task)
                run_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to run task '{task.name}': {e}",
                    level=messages.ERROR
                )
        if run_count:
            self.message_user(
                request,
                _(f"{run_count} task(s) triggered successfully."),
                level=messages.SUCCESS
            )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/run-now/",
                self.admin_site.admin_view(self.run_now_view),
                name="run_news_task_now",
            ),
        ]
        return custom_urls + urls

    def run_now_view(self, request, object_id):
        task = self.get_object(request, object_id)
        if not task:
            self.message_user(request, "Task not found.", level=messages.ERROR)
            return redirect("..")
        try:
            current_app.send_task(task.task)
            self.message_user(
                request,
                f"Task '{task.name}' triggered successfully.",
                level=messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                f"Failed to run task '{task.name}': {e}",
                level=messages.ERROR
            )
        return redirect("..")


class CustomIntervalScheduleAdmin(IntervalScheduleAdmin):
    """
    Custom admin for interval schedules with inline instructions.
    """
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Fetch Intervals"
        extra_context["help_text"] = (
            "<div style='padding:10px; background:#fff8e6; border-left: 5px "
            "solid #ff9900;'>"
            "<strong>Instructions:</strong><br>"
            "These define how often news tasks repeat. Changing an interval "
            "will affect all tasks using it."
            "</div>"
        )
        return super().changelist_view(request, extra_context=extra_context)


# Unregister defaults to avoid conflicts
for model in [PeriodicTask, IntervalSchedule]:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Re-register with custom admin classes
admin.site.register(PeriodicTask, CustomPeriodicTaskAdmin)
admin.site.register(IntervalSchedule, CustomIntervalScheduleAdmin)
