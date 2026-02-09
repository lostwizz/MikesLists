'''
app_core.tests.test_template_inheritance
/srv/django/MikesLists_dev/app_core/tests/test_template_inheritance.py


'''


from pathlib import Path
from django.test import TestCase, RequestFactory, override_settings
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

# Create test templates at import time
TEST_TEMPLATE_DIR = Path(__file__).resolve().parent / "tmp_inheritance_templates"
TEST_TEMPLATE_DIR.mkdir(exist_ok=True)

# Base template
(BASE_TEMPLATE_DIR := TEST_TEMPLATE_DIR / "base_test.html").write_text(
    "{% block content %}BASE: {{ env }}{% endblock %}"
)

# Child template
(CHILD_TEMPLATE_DIR := TEST_TEMPLATE_DIR / "child_test.html").write_text(
    "{% extends 'base_test.html' %}{% block content %}CHILD: {{ env }}{% endblock %}"
)

TEST_TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [
        settings.BASE_DIR / "templates",
        TEST_TEMPLATE_DIR,
    ],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "app_core.context_processors.export_env_vars",
            "app_core.context_processors.user_info",
        ],
    },
}]


class TestTemplateInheritance(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(ENV_NAME="dev", TEMPLATES=TEST_TEMPLATES)
    def test_child_template_inherits_env(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        output = render_to_string("child_test.html", {}, request=request)
        assert output == "CHILD: dev"

    @override_settings(ENV_NAME="live", TEMPLATES=TEST_TEMPLATES)
    def test_base_template_renders_env(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        output = render_to_string("base_test.html", {}, request=request)
        assert output == "BASE: live"
