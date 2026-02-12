import types
from unittest.mock import patch, MagicMock

import pytest
from django.test import RequestFactory

from app_core.context_processors import export_env_vars, user_info


# ----------------------------------------------------------------------
# export_env_vars
# ----------------------------------------------------------------------
@patch("app_core.context_processors.get_env", return_value="dev-env")
def test_export_env_vars(mock_get_env):
    req = RequestFactory().get("/")
    result = export_env_vars(req)

    assert result == {"env": "dev-env"}
    mock_get_env.assert_called_once()


# ----------------------------------------------------------------------
# user_info — authenticated user
# ----------------------------------------------------------------------
@patch("app_core.context_processors.get_env", return_value="prod-env")
def test_user_info_authenticated_remote_addr(mock_get_env):
    req = RequestFactory().get("/")
    req.META["REMOTE_ADDR"] = "10.0.0.5"

    # Fake user object
    user = types.SimpleNamespace(
        is_authenticated=True,
        username="mike",
        profile="PROFILE_OBJ",
    )
    req.user = user

    result = user_info(req)

    assert result["sidebar_username"] == "mike"
    assert result["sidebar_ip"] == "10.0.0.5"
    assert result["sidebar_env"] == "prod-env"
    assert result["user_profile"] == "PROFILE_OBJ"


# ----------------------------------------------------------------------
# user_info — authenticated with X‑Forwarded‑For
# ----------------------------------------------------------------------
@patch("app_core.context_processors.get_env", return_value="prod-env")
def test_user_info_authenticated_xff(mock_get_env):
    req = RequestFactory().get("/")
    req.META["HTTP_X_FORWARDED_FOR"] = "1.2.3.4, 5.6.7.8"

    user = types.SimpleNamespace(
        is_authenticated=True,
        username="alice",
        profile=None,
    )
    req.user = user

    result = user_info(req)

    assert result["sidebar_username"] == "alice"
    assert result["sidebar_ip"] == "1.2.3.4"  # first IP extracted
    assert result["sidebar_env"] == "prod-env"
    assert result["user_profile"] is None


# ----------------------------------------------------------------------
# user_info — unauthenticated user
# ----------------------------------------------------------------------
def test_user_info_unauthenticated():
    req = RequestFactory().get("/")
    req.user = types.SimpleNamespace(is_authenticated=False)

    result = user_info(req)

    assert result == {}  # early return
