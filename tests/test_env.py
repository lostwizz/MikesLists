from django.test import TestCase, override_settings
from app_core.utils.env import get_env, is_dev, is_live


class EnvironmentLogicTests(TestCase):

    @override_settings(ENV_NAME="dev")
    def test_dev_environment(self):
        self.assertEqual(get_env(), "dev")
        self.assertTrue(is_dev())
        self.assertFalse(is_live())

    @override_settings(ENV_NAME="live")
    def test_live_environment(self):
        self.assertEqual(get_env(), "live")
        self.assertTrue(is_live())
        self.assertFalse(is_dev())

    @override_settings(ENV_NAME="INVALID")
    def test_fallback_logic(self):
        # Should fallback to DEV if an unknown string is provided
        self.assertEqual(get_env(), "dev")
        self.assertTrue(is_dev())
