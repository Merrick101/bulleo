from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, get_user
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm


def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after signup
            return redirect('users:profile')  # Redirect to profile page

    else:
        form = UserCreationForm()

    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # Redirect to homepage after login
    else:
        form = AuthenticationForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')  # Redirect to profile page

    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/profile.html', {'form': form, 'profile': profile})


def logout_view(request):
    logout(request)
    return redirect("home")  # Redirect to homepage after logout


def check_login_status(request):
    """Checks if the user is authenticated after OAuth login."""
    return JsonResponse({"is_authenticated": request.user.is_authenticated})
