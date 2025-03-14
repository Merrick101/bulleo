from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import Profile, Category, Notification
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

    preferred_category_names = list(profile.preferred_categories.all().values_list('name', flat=True))

    return render(request, "users/profile.html", {
        "form": form,
        "profile": profile,
        "preferred_category_names": preferred_category_names,
    })


@login_required
def update_email(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_email = request.POST.get('email', '').strip()
        if new_email:
            if new_email == request.user.email:
                return JsonResponse({'success': False, 'error': 'New email must be different from your current email.'})
            User = get_user_model()
            if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                return JsonResponse({'success': False, 'error': 'This email is already in use.'})
            request.user.email = new_email
            try:
                request.user.save()
                return JsonResponse({'success': True, 'message': 'Email updated successfully!'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'error': 'Email cannot be empty.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


@login_required
def update_password(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_new_password = request.POST.get('confirm_new_password', '')

        # Check if any password field is filled
        if current_password or new_password or confirm_new_password:
            if not current_password:
                return JsonResponse({'success': False, 'error': 'Current password is required to change your password.'})
            if not request.user.check_password(current_password):
                return JsonResponse({'success': False, 'error': 'Current password is incorrect.'})
            if new_password != confirm_new_password:
                return JsonResponse({'success': False, 'error': 'New passwords do not match.'})
            if not new_password:
                return JsonResponse({'success': False, 'error': 'New password cannot be empty.'})
            try:
                request.user.set_password(new_password)
                request.user.save()
                # Update the session so the user doesn't get logged out
                update_session_auth_hash(request, request.user)
                return JsonResponse({'success': True, 'message': 'Password updated successfully!'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'error': 'No password change requested.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


@login_required
def update_notifications(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Check if the checkbox was checked. If not present, it's unchecked.
        enabled = request.POST.get('notification_preferences')
        notifications_enabled = True if enabled is not None else False
        profile = request.user.profile
        profile.notifications_enabled = notifications_enabled
        try:
            profile.save()
            return JsonResponse({
                'success': True,
                'message': 'Notification preferences updated successfully!',
                'notifications_enabled': notifications_enabled
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


@login_required
def update_username(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_username = request.POST.get('username', '').strip()
        if new_username:
            request.user.username = new_username
            try:
                request.user.save()
                return JsonResponse({'success': True, 'message': "Username updated successfully!"})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'error': "Username cannot be empty."})
    return JsonResponse({'success': False, 'error': "Invalid request."}, status=400)


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


@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(read=False).update(read=True)
    return JsonResponse({'success': True})


def test_onboarding(request):
    """
    Temporary test view for category selection.
    """
    categories = Category.objects.all()
    return render(request, "onboarding/category_selection.html", {"categories": categories})
