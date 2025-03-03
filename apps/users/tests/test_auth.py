from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

User = get_user_model()


class UserAuthenticationTests(TestCase):

    def setUp(self):
        # Create a test user for login tests.
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="ComplexPass123!"
        )
        # Create a dummy SocialApp for Google so that Allauth's provider tag works.
        self.site = Site.objects.get_current()
        self.social_app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="dummy-client-id",
            secret="dummy-secret"
        )
        self.social_app.sites.add(self.site)

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
        response = self.client.post(signup_url, data, follow=True)
        self.assertTrue(response.redirect_chain)
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
        self.assertEqual(response.status_code, 200)
        # Expect the Allauth SignupForm to produce this error on password2.
        self.assertFormError(response, 'form', 'password2', "You must type the same password each time.")

    def test_login_success(self):
        """
        Test that a user can log in with correct credentials.
        """
        login_url = reverse('account_login')
        data = {
            'login': self.user.email,  # Using email for login.
            'password': 'ComplexPass123!'
        }
        response = self.client.post(login_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Verify that the session now indicates a logged-in user.
        self.assertTrue('_auth_user_id' in self.client.session)
        # Optionally, verify that the final URL is the LOGIN_REDIRECT_URL.
        self.assertEqual(response.request.get('PATH_INFO'), '/')

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
        self.assertEqual(response.status_code, 200)
        # Check for a non-field error; adjust the expected error message to match Allauth's output.
        self.assertFormError(response, 'form', None, "The email address and/or password you specified are not correct.")

    def test_logout(self):
        """
        Test that a logged-in user can log out.
        """
        self.client.login(username=self.user.username, password="ComplexPass123!")
        logout_url = reverse('account_logout')
        response = self.client.post(logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_access_requires_login(self):
        """
        Test that an unauthenticated user cannot access the profile page.
        """
        profile_url = reverse('users:profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 302)


class SocialLoginTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()
        self.social_app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="dummy-client-id",
            secret="dummy-secret"
        )
        self.social_app.sites.add(self.site)

    def test_provider_login_url_generation(self):
        """
        Test that the social login URL for Google is generated correctly.
        """
        # Use the URL name provided by Allauth for Google login; typically 'google_login'
        google_login_url = reverse('google_login')
        self.assertTrue(google_login_url)


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="ComplexPass123!"
        )

    def test_password_reset_valid_email(self):
        """
        Ensure that a POST with a valid email triggers a password reset email.
        """
        reset_url = reverse('account_reset_password')
        data = {'email': self.user.email}
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_password_reset_invalid_email(self):
        """
        Ensure that a POST with a non-existent email also sends an email for security reasons.
        """
        reset_url = reverse('account_reset_password')
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(reset_url, data)
        self.assertEqual(response.status_code, 302)
        # Since Django's password reset view is ambiguous for security, it may send an email even if the address doesn't exist.
        self.assertEqual(len(mail.outbox), 1)
