#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_sync_permissions.py
Tests for the sync_permissions management command
"""
###############################################################################

import pytest
from unittest.mock import patch
from django.core.management import call_command


@pytest.mark.django_db
def test_sync_permissions_command_outputs_and_calls():
    # Patch the sync function so we don't hit the DB
    with patch("app_accounts.management.commands.sync_permissions.sync_group_permissions") as mock_sync:
        # Capture stdout
        from io import StringIO
        out = StringIO()

        call_command("sync_permissions", stdout=out)

        output = out.getvalue()

        # Ensure both roles were processed
        assert "Processing Role: Admin_Manager..." in output
        assert "Processing Role: Staff_Editor..." in output

        # Ensure final success message printed
        assert "All groups synced across all apps." in output

        # Ensure sync_group_permissions was called twice
        assert mock_sync.call_count == 2

        # Validate the exact calls
        mock_sync.assert_any_call(
            "Admin_Manager",
            {
                "app_accounts": ["view_profile", "change_profile"],
                "app_blog": ["add_post", "change_post", "delete_post"],
                "app_reports": ["view_analytics"],
            },
        )

        mock_sync.assert_any_call(
            "Staff_Editor",
            {
                "app_accounts": ["view_profile"],
                "app_blog": ["add_post", "change_post"],
            },
        )
