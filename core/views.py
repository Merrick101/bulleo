"""
A Django view to handle admin logout.
Located at: core/views.py
"""

from django.contrib.auth import logout  # NOQA
from django.shortcuts import redirect


def custom_logout_redirect(request):
    """
    Redirects users to appropriate post-logout destinations.
    """
    referer = request.META.get("HTTP_REFERER", "")
    if "/admin" in referer:
        return redirect("/admin/login/")
    return redirect("/")
