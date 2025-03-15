from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.users.models import Profile

User = get_user_model()


class ProfileViewTests(TestCase):
    def setUp(self):
        # Create a test user; the signals will automatically create a Profile.
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.profile = self.user.profile  # Ensure the profile exists.
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_profile_view_get(self):
        """
        Verify that an authenticated user can access the profile page,
        the correct template is used, and expected context variables are present.
        """
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

        # Check for expected context variables.
        self.assertIn('profile', response.context)
        self.assertIn('saved_articles', response.context)
        self.assertIn('upvoted_articles', response.context)
        self.assertIn('comments', response.context)
        self.assertIn('preferred_category_names', response.context)
        self.assertIn('categories', response.context)

    def test_profile_page_content(self):
        """
        Check that the rendered profile page includes the user's username and expected text.
        """
        url = reverse('users:profile')
        response = self.client.get(url)
        content = response.content.decode('utf-8')
        self.assertIn(self.user.username, content)
        self.assertIn("Profile Settings", content)
