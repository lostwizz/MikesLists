from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from app_core.urls import *

class TestUrls(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_admin_url(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)  # Redirects to admin login page

    def test_status_url(self):
        response = self.client.get(reverse('status_dashboard'))
        self.assertIn(response.status_code, [200,302])  # Should return a 200 status code

    def test_health_url(self):
        response = self.client.get(reverse('health_check'))
        self.assertIn(response.status_code, [200,503])  # Should return a 200 status code

    def test_root_url(self):
        response = self.client.get(reverse('root_redirect'))
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard

    def test_accounts_url(self):
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard


    def test_password_reset_url(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)  # Should return a 200 status code

    def test_login_url(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)  # Should return a 200 status code

    def test_logout_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)  # Redirects to login page


#cant do this yet - no code in ToDo app
    # def test_todo_url(self):
    #     response = self.client.get(reverse('todo'))
    #     self.assertEqual(response.status_code, 200)  # Should return a 200 status code
