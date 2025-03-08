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
            raise forms.ValidationError("An email address is required to create an account.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please use a different one.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "preferred_categories"]


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Write a comment..."}),
        max_length=1000
    )

    parent_comment_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Comment
        fields = ["content", "parent_comment_id"]

    def clean_parent_comment_id(self):
        parent_comment_id = self.cleaned_data.get("parent_comment_id")
        if parent_comment_id:
            # Ensure that the parent comment exists
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id)
            except Comment.DoesNotExist:
                raise forms.ValidationError("The parent comment does not exist.")
            # Optional: You could add more validation, like checking if it's not a reply to a reply.
            if parent_comment.is_reply():
                raise forms.ValidationError("You cannot reply to a reply.")
        return parent_comment_id
