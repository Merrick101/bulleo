"""
Forms for user authentication, profile editing, account deletion, and comments.
Located at: apps/users/forms.py
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile, Comment

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError(
                "An email address is required to create an account."
            )
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already in use. Please use a different one."
            )
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "preferred_categories"]
        widgets = {
            'bio': forms.Textarea(
                attrs={'class': 'profile-form-input bio-input', 'rows': 4}
            ),
            'preferred_categories': forms.SelectMultiple(
                attrs={'class': 'profile-form-input categories-select'}
            ),
        }


class NewsPreferencesForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['preferred_categories']  # Categories user can select


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput, label="Confirm with your password"
    )


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 3, "placeholder": "Write a comment..."}
        ),
        max_length=1000
    )
    parent_comment_id = forms.IntegerField(
        required=False, widget=forms.HiddenInput()
    )

    class Meta:
        model = Comment
        fields = ["content", "parent_comment_id"]

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if not content:
            raise forms.ValidationError("Comment cannot be empty.")
        return content

    def clean_parent_comment_id(self):
        parent_comment_id = self.cleaned_data.get("parent_comment_id")
        return parent_comment_id
