# app_core.tests.test_context_processors
# /srv/django/MikesLists_dev/app_core/tests/test_context_processors.py


from django.test import TestCase, Client, override_settings, RequestFactory
from django.urls import reverse

from app_core.context_processors import export_env_vars, user_info
from app_accounts.models import Profile
from django.contrib.auth.models import AnonymousUser, User

# from app_core.urls import *

class TestUserInfo(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="mike", password="x")

    def test_user_info_anonymous(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        result = user_info(request)
        assert result == {}

    @override_settings(ENV_NAME="dev")
    def test_user_info_authenticated_remote_addr(self):
        request = self.factory.get("/", REMOTE_ADDR="123.45.67.89")
        request.user = self.user

        profile = Profile.objects.get(user=self.user)

        result = user_info(request)
        assert result["sidebar_username"] == "mike"
        assert result["sidebar_ip"] == "123.45.67.89"
        assert result["sidebar_env"] == "dev"
        assert result["user_profile"] == profile





    @override_settings(ENV_NAME="live")
    def test_user_info_authenticated_forwarded_for(self):
        request = self.factory.get("/", HTTP_X_FORWARDED_FOR="10.0.0.1, 10.0.0.2")
        request.user = self.user
        result = user_info(request)
        assert result["sidebar_ip"] == "10.0.0.1"
        assert result["sidebar_env"] == "live"

    @override_settings(ENV_NAME="dev")
    def test_user_info_with_profile(self):
        request = self.factory.get("/", REMOTE_ADDR="1.2.3.4")
        request.user = self.user

        profile = Profile.objects.get(user=self.user)

        result = user_info(request)
        assert result["user_profile"] == profile






class TestExportEnvVars(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(ENV_NAME="dev")
    def test_export_env_vars_dev(self):
        request = self.factory.get("/")
        result = export_env_vars(request)
        assert result == {"env": "dev"}

    @override_settings(ENV_NAME="live")
    def test_export_env_vars_live(self):
        request = self.factory.get("/")
        result = export_env_vars(request)
        assert result == {"env": "live"}

    @override_settings(ENV_NAME="test")
    def test_export_env_vars_test(self):
        request = self.factory.get("/")
        result = export_env_vars(request)
        assert result == {"env": "test"}
