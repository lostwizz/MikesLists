import pytest
from unittest.mock import patch
from app_ToDo.apps import run_setup_logic


@pytest.mark.django_db
def test_run_setup_logic_calls_assign_permissions():
    """Covers the normal path where call_command succeeds."""
    with patch("django.core.management.call_command") as mock_call:
        run_setup_logic(sender=None)

    mock_call.assert_called_once_with("assign_permissions")


@pytest.mark.django_db
def test_run_setup_logic_exception_path(capsys):
    """Covers the except block when call_command raises an error."""
    with patch("django.core.management.call_command", side_effect=Exception("boom")):
        run_setup_logic(sender=None)

    captured = capsys.readouterr()
    assert "Failed to run permissions setup" in captured.out
