'''
app_core.tests.test_sidebar_rendering
/srv/django/MikesLists_dev/app_core/tests/test_sidebar_rendering.py


'''
__version__ = "0.0.0.000064-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 21:40:05"



from django.test import TestCase, RequestFactory, override_settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from app_accounts.models import Profile

TEST_TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "app_core.context_processors.user_info",
            ]
        },
    }
]




class TestSidebarRendering(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(ENV_NAME="dev", TEMPLATES=TEST_TEMPLATES)
    def test_sidebar_anonymous(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        html = render_to_string("app_core/partials/sidebar.html", {}, request=request)

        assert "Guest" in html or "sidebar_username" not in html




    @override_settings(TEMPLATES=TEST_TEMPLATES)
    def test_sidebar_authenticated(self):
        user = User.objects.create_user(username="mike", password="x")
        profile = Profile.objects.get(user=user)
        self.assertIsInstance(profile, Profile, "profile is not an instance of Profile")

        request = self.factory.get("/", REMOTE_ADDR="1.2.3.4")
        request.user = user

        html = render_to_string("app_core/partials/sidebar.html", {}, request=request)

        assert "mike" in html
        assert "1.2.3.4" in html
        assert "dev" in html
