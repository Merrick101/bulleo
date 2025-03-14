from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import Profile, Category, Notification, Comment
from news.models import Article
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
    categories = Category.objects.all()  # Add this line

    return render(request, "users/profile.html", {
        "form": form,
        "profile": profile,
        "preferred_category_names": preferred_category_names,
        "categories": categories,   # And pass it to the template
    })


@login_required
def update_username(request):
    """
    Updates the user's username.
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_username = request.POST.get('username', '').strip()

        if not new_username:
            return JsonResponse({'success': False, 'error': "Username cannot be empty."})

        try:
            request.user.username = new_username
            request.user.save()
            return JsonResponse({'success': True, 'message': "Username updated successfully!", 'new_username': request.user.username})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': "Invalid request."}, status=400)


@login_required
def update_email(request):
    """
    Updates the user's email address.
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_email = request.POST.get('email', '').strip()

        if not new_email:
            return JsonResponse({'success': False, 'error': 'Email cannot be empty.'})
        if new_email == request.user.email:
            return JsonResponse({'success': False, 'error': 'New email must be different from your current email.'})
        if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
            return JsonResponse({'success': False, 'error': 'This email is already in use.'})

        try:
            request.user.email = new_email
            request.user.save()
            return JsonResponse({'success': True, 'message': 'Email updated successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


@login_required
def update_password(request):
    """
    Updates the user's password securely.
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_new_password = request.POST.get('confirm_new_password', '')

        if not current_password:
            return JsonResponse({'success': False, 'error': 'Current password is required.'})
        if not request.user.check_password(current_password):
            return JsonResponse({'success': False, 'error': 'Current password is incorrect.'})
        if new_password != confirm_new_password:
            return JsonResponse({'success': False, 'error': 'New passwords do not match.'})
        if not new_password:
            return JsonResponse({'success': False, 'error': 'New password cannot be empty.'})

        try:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            return JsonResponse({'success': True, 'message': 'Password updated successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


@login_required
def update_notifications(request):
    """
    Updates the user's notification preferences.
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        profile = request.user.profile
        profile.notifications_enabled = request.POST.get('notification_preferences') is not None

        try:
            profile.save()
            return JsonResponse({'success': True, 'message': 'Notification preferences updated!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


@login_required
def remove_saved_article(request):
    """
    Removes an article from the user's saved list.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        article_id = request.POST.get("article_id")
        article = get_object_or_404(Article, id=article_id)

        if request.user in article.saves.all():
            article.saves.remove(request.user)
            return JsonResponse({"success": True, "message": "Article removed from saved."})
        else:
            return JsonResponse({"success": False, "error": "Article not found in saved list."})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def remove_upvoted_article(request):
    """
    Removes an article from the user's upvoted list.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        article_id = request.POST.get("article_id")
        article = get_object_or_404(Article, id=article_id)

        if request.user in article.likes.all():
            article.likes.remove(request.user)
            return JsonResponse({"success": True, "message": "Upvote removed."})
        else:
            return JsonResponse({"success": False, "error": "Article not found in upvoted list."})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def remove_comment(request):
    """
    Marks a comment as deleted instead of removing it completely.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        comment_id = request.POST.get("comment_id")
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)

        comment.delete()  # Uses the overridden `delete()` method
        return JsonResponse({"success": True, "message": "Comment deleted."})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def clear_saved_articles(request):
    """
    Clears all saved articles for the user.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        request.user.saved_articles.clear()
        return JsonResponse({"success": True, "message": "All saved articles cleared."})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def clear_upvoted_articles(request):
    """
    Clears all upvoted articles for the user.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        request.user.liked_articles.clear()
        return JsonResponse({"success": True, "message": "All upvoted articles cleared."})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def delete_account(request):
    """
    Handles secure account deletion.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        password = request.POST.get("password", "").strip()

        if not request.user.check_password(password):
            return JsonResponse({"success": False, "error": "Incorrect password."})

        try:
            request.user.delete()
            logout(request)
            return JsonResponse({"success": True, "message": "Account deleted successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def onboarding(request):
    """
    Handles category selection during onboarding.
    Allows users to select any number of categories, or skip.
    """
    if request.method == "POST":
        selected = request.POST.get("categories", "")
        selected_ids = [int(cid) for cid in selected.split(",") if cid]

        # Save the selected categories to the user's profile, even if empty
        profile = request.user.profile
        profile.preferred_categories.set(selected_ids)
        profile.save()

        messages.success(request, "Your categories have been saved.")
        return redirect("home")
    else:
        categories = Category.objects.all()
        return render(request, "onboarding/category_selection.html", {"categories": categories})


@login_required
def preferences_update(request):
    """
    Updates the user's preferred categories based on the News Feed Preferences form.
    Accepts AJAX POST requests.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        selected_ids = request.POST.getlist("preferred_categories")  # Get list of selected category IDs
        profile = request.user.profile
        profile.preferred_categories.set(selected_ids)  # Update preferred categories
        profile.save()

        return JsonResponse({"success": True, "message": "Preferences updated successfully."})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def toggle_notifications(request):
    """
    Handles enabling/disabling notifications for the user.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            data = json.loads(request.body)
            enabled = data.get("enabled", True)  # Default to True if not provided
            profile = request.user.profile
            profile.notifications_enabled = enabled
            profile.save()

            return JsonResponse({"success": True, "notifications_enabled": profile.notifications_enabled})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def mark_all_notifications_read(request):
    """
    Marks all unread notifications as read for the logged-in user.
    """
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        request.user.notifications.filter(read=False).update(read=True)
        return JsonResponse({'success': True, 'message': "All notifications marked as read."})

    return JsonResponse({'success': False, 'error': "Invalid request."}, status=400)


def test_onboarding(request):
    """
    Temporary test view for category selection.
    """
    categories = Category.objects.all()
    return render(request, "onboarding/category_selection.html", {"categories": categories})


def logout_view(request):
    """
    Logs out the user and redirects to the home page.
    """
    logout(request)
    return redirect("home")
