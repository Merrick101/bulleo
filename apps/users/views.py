from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile

# Create your views here.


def login_view(request):
    return render(request, 'users/login.html')


@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')  # Redirect to profile page

    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/profile.html', {'form': form, 'profile': profile})
