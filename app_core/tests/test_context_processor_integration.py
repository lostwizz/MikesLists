import os
from pathlib import Path

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User, AnonymousUser
from django.template.loader import render_to_string
from django.conf import settings

from app_accounts.models import Profile


# ----------------------------------------------------------------------
# CREATE TEST TEMPLATE DIRECTORY AT IMPORT TIME
# ----------------------------------------------------------------------

TEST_TEMPLATE_DIR = Path(__file__).resolve().parent / "tmp_test_templates"
TEST_TEMPLATE_DIR.mkdir(exist_ok=True)

TEST_TEMPLATE_PATH = TEST_TEMPLATE_DIR / "cp_test.html"
with open(TEST_TEMPLATE_PATH, "w") as f:
    f.write("{{ env }}|{{ sidebar_username }}|{{ sidebar_ip }}|{{ sidebar_env }}")


# Dummy processor for interaction tests
def dummy_processor(request):
    return {"dummy_value": "XYZ", "env": "dummy-env"}


# ----------------------------------------------------------------------
# BASE TEMPLATE SETTINGS (mirrors your real project + test templates)
# ----------------------------------------------------------------------

TEST_TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [
        settings.BASE_DIR / "templates",   # your real templates
        TEST_TEMPLATE_DIR,                 # test template directory
    ],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "app_core.context_processors.export_env_vars",
            "app_core.context_processors.user_info",
        ],
    },
}]


class TestContextProcessorIntegration(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    # ------------------------------------------------------------------
    # BASIC TESTS
    # ------------------------------------------------------------------

    @override_settings(ENV_NAME="dev", TEMPLATES=TEST_TEMPLATES)
    def test_template_renders_with_anonymous_user(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        output = render_to_string("cp_test.html", {}, request=request)
        assert output == "dev|||"

    @override_settings(ENV_NAME="live", TEMPLATES=TEST_TEMPLATES)
    def test_template_renders_with_authenticated_user(self):
        user = User.objects.create_user(username="mike", password="x")
        Profile.objects.get(user=user)

        request = self.factory.get("/", REMOTE_ADDR="1.2.3.4")
        request.user = user

        output = render_to_string("cp_test.html", {}, request=request)
        assert output == "live|mike|1.2.3.4|live"

    # ------------------------------------------------------------------
    # FORWARDED IP HEADER
    # ------------------------------------------------------------------

    @override_settings(ENV_NAME="dev", TEMPLATES=TEST_TEMPLATES)
    def test_forwarded_for_header(self):
        user = User.objects.create_user(username="mike", password="x")
        Profile.objects.get(user=user)

        request = self.factory.get("/", HTTP_X_FORWARDED_FOR="10.0.0.1, 10.0.0.2")
        request.user = user

        output = render_to_string("cp_test.html", {}, request=request)
        assert output == "dev|mike|10.0.0.1|dev"

    # ------------------------------------------------------------------
    # MISSING REMOTE_ADDR
    # ------------------------------------------------------------------

    @override_settings(ENV_NAME="dev", TEMPLATES=TEST_TEMPLATES)
    def test_missing_remote_addr(self):
        user = User.objects.create_user(username="mike", password="x")
        Profile.objects.get(user=user)

        request = self.factory.get("/")
        request.META.pop("REMOTE_ADDR", None)   # remove default 127.0.0.1
        request.user = user

        output = render_to_string("cp_test.html", {}, request=request)
        assert output == "dev|mike||dev"

    # ------------------------------------------------------------------
    # TEMPLATE VARIABLE OVERRIDING
    # ------------------------------------------------------------------

    @override_settings(ENV_NAME="dev", TEMPLATES=TEST_TEMPLATES)
    def test_template_variable_overrides_context_processor(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        output = render_to_string("cp_test.html", {"env": "OVERRIDE"}, request=request)
        assert output.startswith("OVERRIDE")

    # ------------------------------------------------------------------
    # MULTIPLE CONTEXT PROCESSORS INTERACTION
    # ------------------------------------------------------------------

    @override_settings(
        ENV_NAME="live",
        TEMPLATES=[{
            **TEST_TEMPLATES[0],
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "app_core.context_processors.export_env_vars",
                    "app_core.context_processors.user_info",
                    "app_core.tests.test_context_processor_integration.dummy_processor",
                ]
            },
        }],
    )
    def test_multiple_context_processors_interaction(self):
        user = User.objects.create_user(username="mike", password="x")
        Profile.objects.get(user=user)

        request = self.factory.get("/", REMOTE_ADDR="9.9.9.9")
        request.user = user

        output = render_to_string("cp_test.html", {}, request=request)

        assert output.startswith("dummy-env")
        assert "|mike|9.9.9.9|" in output
