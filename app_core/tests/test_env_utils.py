# app_core/tests/test_env_utils.py
'''
app_core.tests.test_env_utils
/srv/django/MikesLists_dev/app_core/tests/test_env_utils.py



'''

from django.test import TestCase, override_settings
from app_core.utils.env import get_env, is_dev


class TestEnvUtils(TestCase):

    @override_settings(ENV_NAME="dev")
    def test_get_env_dev(self):
        assert get_env() == "dev"
        assert is_dev() is True

    @override_settings(ENV_NAME="live")
    def test_get_env_live(self):
        assert get_env() == "live"
        assert is_dev() is False

    @override_settings(ENV_NAME="test")
    def test_get_env_test(self):
        assert get_env() == "test"
        assert is_dev() is False

    @override_settings()  # ENV_NAME missing
    def test_get_env_default(self):
        assert get_env() == "dev"
        assert is_dev() is True
