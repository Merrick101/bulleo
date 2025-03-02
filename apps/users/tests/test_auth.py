from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAuthenticationTests(TestCase):

    def setUp(self):
        # Create a test user for login tests
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="ComplexPass123!"
        )

    def test_signup_success(self):
        """
        Test that a new user can sign up successfully.
        """
        signup_url = reverse('account_signup')
        data = {
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(signup_url, data)
        # Check for redirect (successful signup usually redirects)
        self.assertEqual(response.status_code, 302)
        # Verify that the user now exists
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_signup_invalid(self):
        """
        Test that sign up fails when passwords don't match.
        """
        signup_url = reverse('account_signup')
        data = {
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass123!',
        }
        response = self.client.post(signup_url, data)
        # Should not redirect; should return a 200 with errors in the context.
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn't match.")

    def test_login_success(self):
        """
        Test that a user can log in with correct credentials.
        """
        login_url = reverse('account_login')
        data = {
            'login': self.user.email,  # If using email-based login
            'password': 'ComplexPass123!'
        }
        response = self.client.post(login_url, data)
        # Successful login should redirect to LOGIN_REDIRECT_URL
        self.assertEqual(response.status_code, 302)
        # Verify that the session now indicates a logged-in user.
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_failure(self):
        """
        Test that login fails with incorrect credentials.
        """
        login_url = reverse('account_login')
        data = {
            'login': self.user.email,
            'password': 'WrongPassword'
        }
        response = self.client.post(login_url, data)
        # Login failure should not redirect (status code 200) and should contain an error message.
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The e-mail address and/or password you specified are not correct.")

    def test_logout(self):
        """
        Test that a logged-in user can log out.
        """
        # Log in first
        self.client.login(username=self.user.username, password="ComplexPass123!")
        logout_url = reverse('account_logout')
        response = self.client.post(logout_url)
        # Logout typically redirects to LOGOUT_REDIRECT_URL
        self.assertEqual(response.status_code, 302)
        # Check that the session no longer contains the user.
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_access_requires_login(self):
        """
        Test that an unauthenticated user cannot access the profile page.
        """
        profile_url = reverse('users:profile')
        response = self.client.get(profile_url)
        # Should redirect to the login page
        self.assertEqual(response.status_code, 302)
