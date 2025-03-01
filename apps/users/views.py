from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate
from .models import Profile

User = get_user_model()  # Ensure correct user model


def signup_view(request):
    """Handles user signup through the modal in base.html."""
    from .forms import CustomUserCreationForm  # Import inside function

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Authenticate and log in the user after signup
            authenticated_user = authenticate(username=user.username, password=form.cleaned_data["password1"])
            if authenticated_user:
                login(request, authenticated_user, backend="django.contrib.auth.backends.ModelBackend")

            return redirect("home")  # Redirect back to home page after signup
    return redirect("home")  # If method is GET, simply go back to home


def login_view(request):
    """Handles user login through the modal in base.html."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")  # Ensure backend is specified
            return redirect("home")  # Redirect to homepage after login
    return redirect("home")  # Redirect back to home


@login_required
def profile_view(request):
    """Handles user profile page."""
    from .forms import ProfileForm  # Import inside function

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("users:profile")  # Redirect to profile page

    else:
        form = ProfileForm(instance=profile)

    return render(request, "users/profile.html", {"form": form, "profile": profile})


def logout_view(request):
    """Logs out the user and redirects to home."""
    logout(request)
    return redirect("home")  # Redirect to homepage after logout


def check_login_status(request):
    """Checks if the user is authenticated after OAuth login."""
    return JsonResponse({"is_authenticated": request.user.is_authenticated})
