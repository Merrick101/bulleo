from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from apps.news.forms import ContactForm


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ContactFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('news:contact')

    def test_contact_form_get(self):
        """
        Verify that the contact form page loads properly and uses the correct template.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/contact.html')
        self.assertIsInstance(response.context.get('form'), ContactForm)

    def test_contact_form_valid_submission(self):
        """
        Verify that a valid submission sends an email and redirects appropriately.
        """
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content.',
        }
        response = self.client.post(self.url, data)
        # Check that we redirect after a successful POST
        self.assertEqual(response.status_code, 302)
        # Check that an email was sent (using locmem backend)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Test Subject')
        self.assertIn('Test message content.', email.body)
