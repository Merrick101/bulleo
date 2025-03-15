import cloudinary
cloudinary.config(
    cloud_name='test-cloud',
    api_key='dummy-key',
    api_secret='dummy-secret'
)

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from bs4 import BeautifulSoup

User = get_user_model()


@override_settings(
    CLOUDINARY_CLOUD_NAME='test-cloud',
    CLOUDINARY_API_KEY='dummy-key',
    CLOUDINARY_API_SECRET='dummy-secret'
)
class ProfileAccordionsTest(TestCase):
    def setUp(self):
        # Create a test user. Signals will create the associated profile.
        self.user = User.objects.create_user(
            username='accordiontester',
            email='accordiontester@example.com',
            password='testpassword123'
        )
        self.client = Client()
        self.client.login(username='accordiontester', password='testpassword123')

    def get_soup(self):
        """Helper to fetch the profile page and parse its HTML."""
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Profile page did not load successfully.")
        return BeautifulSoup(response.content, 'html.parser')

    def test_edit_account_details_accordion_exists(self):
        """Check that the Edit Account Details accordion is rendered with its key form."""
        soup = self.get_soup()
        accordion = soup.find(id="accordionEditAccount")
        self.assertIsNotNone(accordion, "Edit Account Details accordion not found.")
        collapse = soup.find(id="collapseEditAccount")
        self.assertIsNotNone(collapse, "Collapse element for Edit Account Details not found.")
        form = accordion.find("form", id="update-username-form")
        self.assertIsNotNone(form, "Username update form not found in Edit Account Details accordion.")

    def test_news_feed_preferences_accordion_exists(self):
        """Verify that the News Feed Preferences accordion is present and contains its form."""
        soup = self.get_soup()
        accordion = soup.find(id="accordionNewsFeed")
        self.assertIsNotNone(accordion, "News Feed Preferences accordion not found.")
        form = accordion.find("form", id="news-feed-preferences-form")
        self.assertIsNotNone(form, "News feed preferences form not found in News Feed Preferences accordion.")

    def test_saved_for_later_accordion_exists(self):
        """Ensure that the Saved for Later accordion is present with a Clear All button."""
        soup = self.get_soup()
        accordion = soup.find(id="accordionSavedForLater")
        self.assertIsNotNone(accordion, "Saved for Later accordion not found.")
        clear_btn = accordion.find("button", id="clear-saved")
        self.assertIsNotNone(clear_btn, "Clear All button for Saved for Later not found.")

    def test_upvoted_articles_accordion_exists(self):
        """Check that the Upvoted Articles accordion is rendered with its Clear All button."""
        soup = self.get_soup()
        accordion = soup.find(id="accordionUpvotedArticles")
        self.assertIsNotNone(accordion, "Upvoted Articles accordion not found.")
        clear_btn = accordion.find("button", id="clear-upvoted")
        self.assertIsNotNone(clear_btn, "Clear All button for Upvoted Articles not found.")

    def test_comment_history_accordion_exists(self):
        """Verify that the Comment History accordion is present with the Clear All Comments button."""
        soup = self.get_soup()
        accordion = soup.find(id="accordionCommentHistory")
        self.assertIsNotNone(accordion, "Comment History accordion not found.")
        clear_btn = accordion.find("button", id="clear-comments-btn")
        self.assertIsNotNone(clear_btn, "Clear All Comments button not found in Comment History accordion.")

    def test_delete_account_accordion_exists(self):
        """Ensure that the Delete Account accordion is rendered with its deletion form."""
        soup = self.get_soup()
        accordion = soup.find(id="accordionDeleteAccount")
        self.assertIsNotNone(accordion, "Delete Account accordion not found.")
        form = accordion.find("form", id="delete-account-form")
        self.assertIsNotNone(form, "Delete account form not found in Delete Account accordion.")
