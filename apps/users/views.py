from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from .models import Profile

User = get_user_model()  # Ensure correct user model


def signup_view(request):
    """
    Handles user signup with enhanced error handling.
    For AJAX requests, returns JSON responses with errors or redirect URL.
    Otherwise, re-renders a dedicated signup modal template with error messages.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            authenticated_user = authenticate(
                username=user.username, password=form.cleaned_data["password1"]
            )
            if authenticated_user:
                login(request, authenticated_user, backend="django.contrib.auth.backends.ModelBackend")
            # AJAX response on success
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "redirect_url": "/"})
            return redirect("home")
        else:
            # AJAX response on error
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                errors = {field: error.get_json_data() for field, error in form.errors.items()}
                return JsonResponse({"success": False, "errors": errors}, status=400)
            # Non-AJAX: Add an error message and re-render the signup modal template
            messages.error(request, "There were errors with your submission. Please correct them below.")
            return render(request, "users/signup_modal.html", {"signup_form": form})
    return redirect("home")


def login_view(request):
    """
    Handles user login.
    (For simplicity, this remains non-AJAX; similar AJAX handling could be implemented if desired.)
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("home")
    return redirect("home")


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


def check_login_status(request):
    """
    Checks whether the user is authenticated.
    """
    return JsonResponse({"is_authenticated": request.user.is_authenticated})
