# app_core/tests/test_env_utils.py
'''
app_core.tests.test_env_utils
/srv/django/MikesLists_dev/app_core/tests/test_env_utils.py



'''

import pytest
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



from app_core.utils.env import (
    AppEnv,
    get_env,
    get_env_enum,
    is_dev,
    is_test,
    is_live,
    is_local_env,
    is_production_env,
)


@pytest.mark.parametrize(
    "env_name, expected_enum",
    [
        ("dev", AppEnv.DEV),
        ("test", AppEnv.TEST),
        ("live", AppEnv.LIVE),
        ("DEV", AppEnv.DEV),
        ("TeSt", AppEnv.TEST),
    ],
)
def test_get_env_enum_valid(env_name, expected_enum):
    with override_settings(ENV_NAME=env_name):
        assert get_env_enum() is expected_enum
        assert get_env() == expected_enum.value


from unittest.mock import patch

@patch("app_core.utils.env.logger")
def test_get_env_enum_missing_defaults_to_dev(mock_logger):
    with override_settings(ENV_NAME=None):
        assert get_env_enum() is AppEnv.DEV

    mock_logger.warning.assert_called_once()
    assert "defaulting to DEV" in mock_logger.warning.call_args[0][0]




@patch("app_core.utils.env.logger")
def test_get_env_enum_unknown_falls_back_to_dev(mock_logger):
    with override_settings(ENV_NAME="weird"):
        assert get_env_enum() is AppEnv.DEV

    mock_logger.warning.assert_called_once()
    assert "Unknown ENV_NAME" in mock_logger.warning.call_args[0][0]




def test_is_dev():
    with override_settings(ENV_NAME="dev"):
        assert is_dev() is True
        assert is_test() is False
        assert is_live() is False


def test_is_test():
    with override_settings(ENV_NAME="test"):
        assert is_test() is True
        assert is_dev() is False
        assert is_live() is False


def test_is_live():
    with override_settings(ENV_NAME="live"):
        assert is_live() is True
        assert is_dev() is False
        assert is_test() is False


def test_is_local_env():
    with override_settings(ENV_NAME="dev"):
        assert is_local_env() is True
    with override_settings(ENV_NAME="test"):
        assert is_local_env() is True
    with override_settings(ENV_NAME="live"):
        assert is_local_env() is False


def test_is_production_env():
    with override_settings(ENV_NAME="live"):
        assert is_production_env() is True
    with override_settings(ENV_NAME="dev"):
        assert is_production_env() is False
