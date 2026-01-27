from django.test import TestCase
from django.urls import reverse, resolve

class RoutingTests(TestCase):
    def test_homepage_status_code(self):
        """Check if the main site still loads after changes"""
        response = self.client.get('/')
        # self.assertEqual(response.status_code, 200)
        # Option A: Check for the redirect specifically
        self.assertEqual(response.status_code, 302)

        # Option B: Follow the redirect to the actual dashboard
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)

    # Uncomment this once you re-enable your ToDo URLs
    # def test_todo_list_accessible(self):
    #    url = reverse('todo:index')
    #    response = self.client.get(url)
    #    self.assertEqual(response.status_code, 200)
