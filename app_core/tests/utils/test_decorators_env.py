from unittest.mock import patch
from django.http import HttpResponseForbidden

from app_core.utils.decorators import (
    require_env,
    require_dev_env,
    require_test_env,
    require_live_env,
    require_non_dev_only,
)
from app_core.utils.env import AppEnv


# ---------------------------------------------------------------------------
# Helper view
# ---------------------------------------------------------------------------

def dummy_view(request):
    return "OK"


# ---------------------------------------------------------------------------
# require_env tests
# ---------------------------------------------------------------------------

@patch("app_core.utils.decorators.get_env_enum")
def test_require_env_allows_correct_env(mock_env):
    mock_env.return_value = AppEnv.DEV

    wrapped = require_env(AppEnv.DEV)(dummy_view)
    result = wrapped(request=None)

    assert result == "OK"


@patch("app_core.utils.decorators.get_env_enum")
def test_require_env_blocks_wrong_env(mock_env):
    mock_env.return_value = AppEnv.LIVE

    wrapped = require_env(AppEnv.DEV)(dummy_view)
    result = wrapped(request=None)

    assert isinstance(result, HttpResponseForbidden)
    assert "dev" in result.content.decode().lower()


# ---------------------------------------------------------------------------
# Convenience decorators
# ---------------------------------------------------------------------------

@patch("app_core.utils.decorators.get_env_enum")
def test_require_dev_env_allows_dev(mock_env):
    mock_env.return_value = AppEnv.DEV
    assert require_dev_env(dummy_view)(None) == "OK"


@patch("app_core.utils.decorators.get_env_enum")
def test_require_dev_env_blocks_non_dev(mock_env):
    mock_env.return_value = AppEnv.LIVE
    result = require_dev_env(dummy_view)(None)
    assert isinstance(result, HttpResponseForbidden)


@patch("app_core.utils.decorators.get_env_enum")
def test_require_test_env(mock_env):
    mock_env.return_value = AppEnv.TEST
    assert require_test_env(dummy_view)(None) == "OK"


@patch("app_core.utils.decorators.get_env_enum")
def test_require_live_env(mock_env):
    mock_env.return_value = AppEnv.LIVE
    assert require_live_env(dummy_view)(None) == "OK"


@patch("app_core.utils.decorators.get_env_enum")
def test_require_non_dev_only_allows_test(mock_env):
    mock_env.return_value = AppEnv.TEST
    assert require_non_dev_only(dummy_view)(None) == "OK"


@patch("app_core.utils.decorators.get_env_enum")
def test_require_non_dev_only_allows_live(mock_env):
    mock_env.return_value = AppEnv.LIVE
    assert require_non_dev_only(dummy_view)(None) == "OK"


@patch("app_core.utils.decorators.get_env_enum")
def test_require_non_dev_only_blocks_dev(mock_env):
    mock_env.return_value = AppEnv.DEV
    result = require_non_dev_only(dummy_view)(None)
    assert isinstance(result, HttpResponseForbidden)
