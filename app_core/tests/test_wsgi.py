import importlib
import os
from unittest.mock import patch, MagicMock

import app_core.wsgi as wsgi_module

import sys


def reload_wsgi_with_env(cwd_value, initial_env=None):
    if initial_env is None:
        initial_env = {}

    # Remove module so reload is clean
    sys.modules.pop("app_core.wsgi", None)

    with patch.dict(os.environ, initial_env, clear=True), \
         patch("os.getcwd", return_value=cwd_value), \
         patch("django.core.wsgi.get_wsgi_application", return_value="APP"), \
         patch("app_core.wsgi.get_wsgi_application", return_value="APP"):

        import app_core.wsgi as wsgi_module
        importlib.reload(wsgi_module)

        return os.environ.get("DJANGO_SETTINGS_MODULE"), wsgi_module.application


def test_wsgi_sets_live_settings():
    setting, app = reload_wsgi_with_env("/srv/live/project")
    assert setting == "settings.live"
    assert app == "APP"


def test_wsgi_sets_test_settings():
    setting, app = reload_wsgi_with_env("/srv/test/project")
    assert setting == "settings.test"
    assert app == "APP"


def test_wsgi_sets_dev_settings():
    setting, app = reload_wsgi_with_env("/srv/dev/project")
    assert setting == "settings.dev"
    assert app == "APP"


def test_wsgi_respects_existing_env():
    setting, app = reload_wsgi_with_env(
        "/srv/anything",
        initial_env={"DJANGO_SETTINGS_MODULE": "already.set"}
    )
    assert setting == "already.set"
    assert app == "APP"
