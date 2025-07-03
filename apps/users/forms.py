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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.article = kwargs.pop("article", None)
        super().__init__(*args, **kwargs)

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if not content:
            raise forms.ValidationError("Comment cannot be empty.")
        return content

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get("content")
        parent_id = cleaned_data.get("parent_comment_id")

        if self.user and self.article and content:
            existing = Comment.objects.filter(
                user=self.user,
                article=self.article,
                content=content,
                parent_id=parent_id,
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError(
                    "You’ve already posted this exact comment."
                )

        return cleaned_data


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={'placeholder': 'Your Name', 'class': 'form-control'}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'placeholder': 'Your Email', 'class': 'form-control'}
        )
    )
    subject = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={'placeholder': 'Subject', 'class': 'form-control'}
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': 'Your Message',
                   'class': 'form-control', 'rows': 5}
        )
    )
