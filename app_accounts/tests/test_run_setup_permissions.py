from unittest.mock import patch
from app_accounts.apps import run_setup_permissions


def test_run_setup_permissions_exception_path(capsys):
    # Patch the real import location
    with patch("app_accounts.permissions.ensure_groups_and_permissions",
               side_effect=Exception("boom")):
        run_setup_permissions(sender=None)

    captured = capsys.readouterr()
    assert "Error during AppAccountsConfig setup: boom" in captured.out
