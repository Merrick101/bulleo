from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Profile, Category, Comment
from .forms import CommentForm
from apps.news.models import Article

User = get_user_model()  # Ensure correct user model


@login_required
def profile_view(request):
    """
    Handles the user profile page.
    """
    from .forms import ProfileForm  # Import inside function to reduce circular dependencies
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("users:profile")
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
    if request.method == "POST":
        selected = request.POST.get("categories", "")
        selected_ids = [int(cid) for cid in selected.split(",") if cid]
        if len(selected_ids) < 3:
            error = "Please select at least 3 categories."
            return render(request, "onboarding/category_selection.html", {"categories": Category.objects.all(), "error": error})
        # Save the selected categories to the user's profile
        profile = request.user.profile
        profile.preferred_categories.set(selected_ids)
        profile.save()
        return redirect("home")
    else:
        categories = Category.objects.all()
        return render(request, "onboarding/category_selection.html", {"categories": categories})


# Temporary test view
def test_onboarding(request):
    # Fetch all categories for testing
    categories = Category.objects.all()
    return render(request, "onboarding/category_selection.html", {"categories": categories})


@login_required
def post_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
            return redirect("news:article_detail", article_id=article.id)

        # If form is invalid, return it to the template with error messages
        return render(request, "news/article_detail.html", {"article": article, "form": form})

    return redirect("news:article_detail", article_id=article.id)
