import importlib
import os
from unittest.mock import patch, MagicMock


def test_asgi_application_loaded_and_env_set():
    # Ensure the env var is cleared so setdefault is exercised
    os.environ.pop("DJANGO_SETTINGS_MODULE", None)

    fake_app = MagicMock()

    # Patch the import source so reload picks it up
    with patch("django.core.asgi.get_asgi_application", return_value=fake_app) as mock_get:
        import app_core.asgi
        importlib.reload(app_core.asgi)

        # Environment variable should now be set
        assert os.environ["DJANGO_SETTINGS_MODULE"] == "app_core.settings"

        # get_asgi_application should have been called at least once
        assert mock_get.call_count >= 1

        # application should be the fake app
        assert app_core.asgi.application is fake_app
