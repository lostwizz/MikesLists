import pytest
from unittest.mock import patch

from django.test import override_settings

from app_core.services.restart_service import (
    restart_allowed,
    perform_restart,
)


def test_restart_allowed_true():
    with override_settings(STATUS_ALLOW_RESTART=True):
        assert restart_allowed() is True


def test_restart_allowed_false():
    with override_settings(STATUS_ALLOW_RESTART=False):
        assert restart_allowed() is False


@override_settings(
    STATUS_RESTART_SCRIPT="/fake/script.sh",
    STATUS_ALLOW_RESTART=True,
)
@patch("os.path.exists", return_value=False)
def test_restart_script_missing(mock_exists):
    success, msg = perform_restart()
    assert success is False
    assert "not found" in msg.lower()


@override_settings(
    STATUS_RESTART_SCRIPT="/fake/script.sh",
    STATUS_ALLOW_RESTART=True,
)
@patch("os.path.exists", return_value=True)
@patch("os.access", return_value=False)
def test_restart_script_not_executable(mock_access, mock_exists):
    success, msg = perform_restart()
    assert success is False
    assert "not executable" in msg.lower()


@override_settings(
    STATUS_RESTART_SCRIPT="/fake/script.sh",
    STATUS_ALLOW_RESTART=True,
)
@patch("os.path.exists", return_value=True)
@patch("os.access", return_value=True)
@patch("app_core.services.restart_service.run")
def test_restart_success(mock_run, mock_access, mock_exists):
    mock_run.return_value.returncode = 0

    success, msg = perform_restart()
    assert success is True
    assert "ok" in msg.lower()


@override_settings(
    STATUS_RESTART_SCRIPT="/fake/script.sh",
    STATUS_ALLOW_RESTART=True,
)
@patch("os.path.exists", return_value=True)
@patch("os.access", return_value=True)
@patch("app_core.services.restart_service.run")
def test_restart_failure(mock_run, mock_access, mock_exists):
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "boom"

    success, msg = perform_restart()
    assert success is False
    assert "failed" in msg.lower()
