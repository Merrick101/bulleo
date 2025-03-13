from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import Profile, Category
from .forms import ProfileForm

User = get_user_model()


@login_required
def profile_view(request):
    """
    Handles the user profile page.
    """
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("users:profile")
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "users/profile.html", {"form": form, "profile": profile})


def logout_view(request):
    """
    Logs out the user and redirects to the home page.
    """
    logout(request)
    return redirect("home")


@login_required
def onboarding(request):
    """
    Handles category selection during onboarding.
    """
    if request.method == "POST":
        selected = request.POST.get("categories", "")
        selected_ids = [int(cid) for cid in selected.split(",") if cid]

        if len(selected_ids) < 3:
            messages.error(request, "Please select at least 3 categories.")
            return render(request, "onboarding/category_selection.html", {"categories": Category.objects.all()})

        # Save the selected categories to the user's profile
        profile = request.user.profile
        profile.preferred_categories.set(selected_ids)
        profile.save()

        messages.success(request, "Your categories have been saved.")
        return redirect("home")
    else:
        categories = Category.objects.all()
        return render(request, "onboarding/category_selection.html", {"categories": categories})


@login_required
def toggle_notifications(request):
    if request.method == "POST":
        data = json.loads(request.body)
        enabled = data.get("enabled", True)
        profile = request.user.profile
        profile.notifications_enabled = enabled
        profile.save()
        return JsonResponse({"success": True, "notifications_enabled": profile.notifications_enabled})
    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


def test_onboarding(request):
    """
    Temporary test view for category selection.
    """
    categories = Category.objects.all()
    return render(request, "onboarding/category_selection.html", {"categories": categories})
