#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_signals_missing_branches.py

Tests for signal handlers that cover edge cases and missing branches.
"""
###############################################################################

import pytest
import logging
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from unittest.mock import patch, MagicMock

from app_accounts.models.signals import create_user_profile, save_user_profile
from app_accounts.models.profile import Profile


@pytest.mark.django_db
def test_create_user_profile_missing_group_sends_email():
    """
    Test that when the 'Read Only' group is missing during user creation,
    an email is sent to admins.
    """
    # Delete the 'Read Only' group
    Group.objects.filter(name="Read Only").delete()

    # Create an admin user to receive the email
    admin = User.objects.create_user(username="admin", is_staff=True, is_superuser=True)
    admin.email = "admin@example.com"
    admin.save()

    with patch("app_accounts.models.signals.send_mail") as mock_send_mail:
        # Create a new user (should trigger the email since group is missing)
        user = User.objects.create_user(username="testuser", password="x")
        assert user

        # Verify email was sent
        assert mock_send_mail.called


@pytest.mark.skip(reason="Logging is commented out in signals.py")
@pytest.mark.django_db
def test_save_user_profile_no_profile_triggers_debug_branch(caplog):
    """
    Test that the save_user_profile signal handler logs a debug message
    when attempting to save a user without a profile.

    Note: Currently skipped because the logging statement is commented out
    in the production code (signals.py line 66).
    """
    pass


@pytest.mark.django_db
def test_create_user_profile_missing_group_no_admins_skips_email():
    """
    Test that when the 'Read Only' group is missing but there are no admin users,
    no email is sent (avoiding errors).
    """
    # Delete the 'Read Only' group
    Group.objects.filter(name="Read Only").delete()

    # Ensure no admin users exist
    User.objects.filter(is_staff=True).delete()
    User.objects.filter(is_superuser=True).delete()

    with patch("app_accounts.models.signals.send_mail") as mock_send_mail:
        # Create a new user
        user = User.objects.create_user(username="testuser", password="x")
        assert user

        # Email should not be sent since there are no admins
        assert not mock_send_mail.called


@pytest.mark.django_db
def test_create_user_profile_created_false_does_nothing():
    """
    Test that the create_user_profile signal does nothing when created=False
    (i.e., when a user is being updated, not created).
    """
    # Create a user first (this will trigger the signal with created=True)
    user = User.objects.create_user(username="u1", password="x")

    # Ensure profile exists
    assert hasattr(user, "profile")
    profile_id = user.profile.id

    # Now save the user again (should trigger signal with created=False)
    user.email = "newemail@example.com"
    user.save()

    # Profile should still be the same one (not recreated)
    user.refresh_from_db()
    assert user.profile.id == profile_id


@pytest.mark.django_db
def test_save_user_profile_no_profile_triggers_debug_branch(
    caplog,
):  # ← Add caplog here
    """
    Test that the save_user_profile signal handler logs a debug message
    when attempting to save a user without a profile.
    """
    from django.db.models.signals import post_save
    from app_accounts.models.signals import create_user_profile, save_user_profile
    import logging

    # Disconnect the profile-creation signal so profile isn't auto-created
    post_save.disconnect(create_user_profile, sender=User)

    try:
        # Create a user WITHOUT auto-created profile
        user = User.objects.create(username="noprof", email="x@example.com")

        # Confirm no profile exists
        assert not hasattr(user, "profile")

        # Capture debug logs - use the root logger
        with caplog.at_level(logging.DEBUG):
            save_user_profile(User, user, created=False)

        # Verify the debug message was logged
        assert "profile not saved" in caplog.text

    finally:
        # Reconnect the signal for other tests
        post_save.connect(create_user_profile, sender=User)
