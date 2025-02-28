from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, get_user
from django.contrib.auth.backends import ModelBackend  # Default Django backend
from allauth.account.auth_backends import AuthenticationBackend  # Allauth backend
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm

# Create your views here.


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


def close_popup(request):
    return render(request, "users/oauth_callback.html")


def oauth_callback(request):
    """
    Handles OAuth callback, logs in the user, and notifies the main window.
    """
    user = get_user(request)

    if user.is_authenticated:
        try:
            login(request, user, backend="allauth.account.auth_backends.AuthenticationBackend")
        except Exception as e:
            print(f"OAuth login error: {e}")
            return redirect("home")  # Redirect if authentication fails

        response_script = """
        <script>
            console.log("✅ OAuth login successful.");
            if (window.opener) {
                console.log("✅ Sending success message to main window...");
                window.opener.postMessage("google-login-success", window.location.origin);
                window.close();
            } else {
                console.warn("⚠️ No opener detected. Using localStorage fallback...");
                localStorage.setItem("googleLoginSuccess", "true");
                window.location.href = "/";
            }
        </script>
        """
        return HttpResponse(response_script)
    else:
        return redirect("home")  # Redirect if authentication failed


def check_login_status(request):
    """
    Checks if the user is authenticated after OAuth login.
    """
    user = get_user(request)

    # Debugging output
    print(f"Check login status: {user.is_authenticated}")

    return JsonResponse({"is_authenticated": user.is_authenticated})
