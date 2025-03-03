from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.users.models import Category

User = get_user_model()


class CategorySelectionTests(TestCase):
    def setUp(self):
        # Use get_or_create so that seeded categories (from migrations) are reused.
        self.cat1, _ = Category.objects.get_or_create(
            name="World News",
            defaults={"slug": "world-news", "order": 1}
        )
        self.cat2, _ = Category.objects.get_or_create(
            name="Politics",
            defaults={"slug": "politics", "order": 2}
        )
        self.cat3, _ = Category.objects.get_or_create(
            name="Business",
            defaults={"slug": "business", "order": 3}
        )
        self.cat4, _ = Category.objects.get_or_create(
            name="Technology",
            defaults={"slug": "technology", "order": 4}
        )
        self.cat5, _ = Category.objects.get_or_create(
            name="Sports",
            defaults={"slug": "sports", "order": 5}
        )
        self.cat6, _ = Category.objects.get_or_create(
            name="Entertainment",
            defaults={"slug": "entertainment", "order": 6}
        )
        # Create and log in a test user.
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="ComplexPass123!"
        )
        self.client.login(username="testuser", password="ComplexPass123!")
        # Assume the URL name for the onboarding page is 'users:onboarding'
        self.url = reverse("users:onboarding")

    def test_get_onboarding_page_authenticated(self):
        """
        Ensure an authenticated user can load the onboarding page successfully.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Check that the page contains a heading or text unique to the onboarding page.
        self.assertContains(response, "Select Your Preferred Categories")

    def test_get_onboarding_page_unauthenticated(self):
        """
        Ensure that unauthenticated users are redirected (to login).
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_post_fewer_than_three_categories(self):
        """
        If the user selects fewer than 3 categories, the view should return an error.
        """
        data = {"categories": f"{self.cat1.id}"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        # Adjust the expected error message to match what your view outputs.
        self.assertContains(response, "Please select at least 3 categories")

    def test_post_three_categories_success(self):
        """
        Test that a user selecting exactly 3 categories is redirected and their preferences are saved.
        """
        data = {"categories": f"{self.cat1.id},{self.cat2.id},{self.cat3.id}"}
        response = self.client.post(self.url, data, follow=True)
        # Expect a redirect after a successful submission.
        self.assertTrue(response.redirect_chain)
        # Reload the user's profile preferences.
        self.user.refresh_from_db()
        selected = list(self.user.profile.preferred_categories.all())
        self.assertEqual(len(selected), 3)
