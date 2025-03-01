from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Profile

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
