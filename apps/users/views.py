"""
Views for user profile management, including updating profile information,
changing username/email/password, managing saved/upvoted articles,
and handling notifications. Also includes onboarding for category selection.
Located at: apps/users/views.py
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    logout, get_user_model,
    update_session_auth_hash
    )
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from allauth.account.utils import send_email_confirmation
from django.conf import settings
from django.http import JsonResponse
import json
from .models import Profile, Comment, ContactMessage
from apps.news.models import Category
from apps.news.models import Article
from .forms import ProfileForm, ContactForm

User = get_user_model()


@login_required
def profile_view(request):
    """
    Handles the user profile page.
    """
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )  # Ensures profile always exists
    form = ProfileForm(
        request.POST or None, request.FILES or None, instance=profile
    )

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("users:profile")
        messages.error(request, "There was an error updating your profile.")

    # Fetch saved (bookmarked) articles
    saved_articles = request.user.saved_articles.all()

    # Fetch upvoted articles
    upvoted_articles = request.user.liked_articles.all()

    # Fetch user comments with related articles
    # (to display article titles in the profile)
    comments = (
        Comment.objects.filter(user=request.user)
        .select_related("article")
        .order_by("-created_at")
        .distinct()
    )

    context = {
        "form": form,
        "profile": profile,
        "saved_articles": saved_articles,
        "upvoted_articles": upvoted_articles,
        "comments": comments,
        "preferred_category_names": list(
            profile.preferred_categories.values_list('name', flat=True)
        ),
        "categories": Category.objects.exclude(name__iexact="General"),
    }

    return render(request, "users/profile.html", context)


@login_required
def update_username(request):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'error': 'Invalid request.'}, status=400
        )

    new_username = request.POST.get('username', '').strip()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Validation
    if not new_username:
        msg = "Username cannot be empty."
        return JsonResponse(
            {'success': False, 'error': msg}
        ) if is_ajax else _reject(request, msg)

    if new_username == request.user.username:
        msg = "No changes detected."
        return JsonResponse(
            {'success': False, 'error': msg}
        ) if is_ajax else _reject(request, msg)

    if User.objects.filter(
        username=new_username
    ).exclude(pk=request.user.pk).exists():
        msg = "This username is already taken."
        return JsonResponse(
            {'success': False, 'error': msg}
        ) if is_ajax else _reject(request, msg)

    # Save
    try:
        request.user.username = new_username
        request.user.save()
        msg = "Username updated successfully!"
        return JsonResponse(
            {'success': True, 'message': msg, 'new_username': new_username}
        ) if is_ajax else _success(request, msg)
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': str(e)}
        ) if is_ajax else _reject(str(e))


def _reject(request, message):
    messages.error(request, message)
    return redirect('users:profile')


def _success(request, message):
    messages.success(request, message)
    return redirect('users:profile')


@login_required
def update_email(request):
    if request.method != 'POST' or request.headers.get(
        'X-Requested-With'
    ) != 'XMLHttpRequest':
        return JsonResponse(
            {'success': False, 'error': 'Invalid request.'}, status=400
        )

    new_email = request.POST.get('email', '').strip()

    # Validation
    if not new_email:
        return JsonResponse(
            {'success': False, 'error': 'Email cannot be empty.'}
        )
    if new_email == request.user.email:
        return JsonResponse(
            {'success': False, 'error': 'No changes detected.'}
        )
    if User.objects.filter(
        email=new_email
    ).exclude(pk=request.user.pk).exists():
        return JsonResponse(
            {'success': False, 'error': 'This email is already in use.'}
        )

    # Save
    try:
        request.user.email = new_email
        request.user.save()
        send_email_confirmation(request, request.user)

        return JsonResponse(
            {'success': True,
             'message': 'Email updated. A confirmation email has been sent.'}
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': str(e)}
        )


@login_required
def update_password(request):
    if request.method != 'POST' or request.headers.get(
        'X-Requested-With'
    ) != 'XMLHttpRequest':
        return JsonResponse(
            {'success': False, 'error': 'Invalid request.'}, status=400
        )

    current = request.POST.get('current_password', '')
    new = request.POST.get('new_password', '')
    confirm = request.POST.get('confirm_new_password', '')

    # Validation
    if not current or not new or not confirm:
        return JsonResponse(
            {'success': False, 'error': 'All fields are required.'}
        )
    if not request.user.check_password(current):
        return JsonResponse(
            {'success': False, 'error': 'Current password is incorrect.'}
        )
    if new != confirm:
        return JsonResponse(
            {'success': False, 'error': 'New passwords do not match.'}
        )
    if new == current:
        return JsonResponse(
            {'success': False, 'error': 'New password must be different.'}
        )

    # Save
    try:
        request.user.set_password(new)
        request.user.save()
        update_session_auth_hash(request, request.user)
        return JsonResponse(
            {'success': True, 'message': 'Password updated successfully!'}
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': str(e)}
        )


@login_required
def update_notifications(request):
    """
    Updates the user's notification preferences.
    """
    if request.method == 'POST' and request.headers.get(
        'X-Requested-With'
    ) == 'XMLHttpRequest':
        profile = request.user.profile
        profile.notifications_enabled = request.POST.get(
            'notification_preferences'
        ) is not None

        try:
            profile.save()
            return JsonResponse(
                {'success': True,
                 'message': 'Notification preferences updated!'}
            )
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse(
        {'success': False, 'error': 'Invalid request.'}, status=400
    )


@login_required
def remove_saved_article(request):
    """Removes an article from the user's saved list."""
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        article_id = request.POST.get("id")
        if not article_id:
            return JsonResponse(
                {"success": False, "error": "Missing article ID"}, status=400
            )

        article = get_object_or_404(Article, id=article_id)
        if request.user in article.saves.all():
            article.saves.remove(request.user)
            return JsonResponse({"success": True})

        return JsonResponse(
            {"success": False, "error": "Article was not saved"}, status=400
        )

    return JsonResponse(
        {"success": False, "error": "Invalid request"}, status=400
    )


@login_required
def remove_upvoted_article(request):
    """
    Removes an article from the user's upvoted list.
    """
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        article_id = request.POST.get("id")
        if not article_id:
            return JsonResponse(
                {"success": False, "error": "Missing article ID"}, status=400
            )

        article = get_object_or_404(Article, id=article_id)

        if request.user in article.likes.all():
            article.likes.remove(request.user)
            return JsonResponse({"success": True})

        return JsonResponse(
            {"success": False, "error": "Article was not upvoted"}, status=400
        )

    return JsonResponse(
        {"success": False, "error": "Invalid request"}, status=400
    )


@login_required
def remove_comment(request):
    """
    Marks a comment as deleted instead of removing it completely.
    """
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        comment_id = request.POST.get("comment_id")
        if not comment_id:
            return JsonResponse(
                {"success": False, "error": "Missing comment ID"}, status=400
            )

        comment = get_object_or_404(
            Comment, id=comment_id, user=request.user
        )

        comment.delete()  # Uses the overridden `delete()` method
        return JsonResponse({"success": True, "message": "Comment deleted."})

    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def clear_saved_articles(request):
    """Clears all saved articles for the user."""
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        request.user.saved_articles.clear()
        request.user.save()  # Ensure user data is saved after clearing
        return JsonResponse(
            {"success": True, "message": "All saved articles cleared."}
        )

    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def clear_upvoted_articles(request):
    """Clears all upvoted articles for the user."""
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        request.user.liked_articles.clear()
        request.user.save()  # Ensure user data is saved after clearing
        return JsonResponse(
            {"success": True, "message": "All upvoted articles cleared."}
        )

    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def clear_comments(request):
    """
    Clears all comments made by the current user.
    Uses the overridden delete() method on Comment which marks them as deleted.
    """
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        user_comments = Comment.objects.filter(user=request.user)
        for comment in user_comments:
            # This will mark the comment as "[Deleted]"
            # per your model override.
            comment.delete()
        return JsonResponse(
            {"success": True, "message": "All comments cleared."}
        )
    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def delete_account(request):
    """
    Handles secure account deletion.
    """
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        password = request.POST.get("password", "").strip()

        if not request.user.check_password(password):
            return JsonResponse(
                {"success": False, "error": "Incorrect password."}
            )
        try:
            request.user.delete()
            logout(request)
            return JsonResponse(
                {"success": True, "message": "Account deleted successfully."}
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


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
        categories = Category.objects.exclude(
            name__iexact="General"
        ).order_by("name")
        return render(
            request, "onboarding/category_selection.html",
            {"categories": categories}
        )


@login_required
def preferences_update(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist("preferred_categories")
        profile = request.user.profile
        profile.preferred_categories.set(selected_ids)
        profile.save()

        # Check if AJAX request, respond accordingly
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success":
                    True, "message": "Preferences updated successfully."}
            )

        messages.success(request, "Preferences updated successfully.")
        return redirect("users:profile")

    # Still reject GET
    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def toggle_notifications(request):
    """
    Handles enabling/disabling notifications for the user.
    """
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        try:
            data = json.loads(request.body)
            # Default to True if not provided
            enabled = data.get("enabled", True)
            profile = request.user.profile
            profile.notifications_enabled = enabled
            profile.save()

            return JsonResponse(
                {"success": True, "notifications_enabled":
                    profile.notifications_enabled}
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def mark_all_notifications_read(request):
    """
    Marks all unread notifications as read for the logged-in user.
    """
    if request.method == "POST" and request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":
        request.user.notifications.filter(read=False).update(read=True)
        return JsonResponse(
            {'success': True, 'message': "All notifications marked as read."}
        )

    return JsonResponse(
        {'success': False, 'error': "Invalid request."}, status=400
    )


def test_onboarding(request):
    """
    Temporary test view for category selection.
    """
    categories = Category.objects.all()
    return render(
        request, "onboarding/category_selection.html",
        {"categories": categories}
    )


def logout_view(request):
    """
    Logs out the user and redirects to the home page.
    """
    logout(request)
    return redirect("home")


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Optional: Save to DB
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            # Compose email content
            full_message = f"Message from {name} ({email}):\n\n{message}"

            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_RECIPIENT_EMAIL],
                fail_silently=False,
            )

            messages.success(
                request, "Thank you for your message."
                "We'll get back to you soon."
            )
            return redirect('users:contact')
    else:
        form = ContactForm()

    return render(request, 'users/contact.html', {'form': form})
