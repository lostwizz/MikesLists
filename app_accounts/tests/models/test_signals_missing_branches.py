#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch

from django.contrib.auth.models import User, Group
from django.core import mail

from app_accounts.models.signals import create_user_profile, save_user_profile


@pytest.mark.django_db
def test_create_user_profile_missing_group_sends_email():
    # Ensure the "Read Only" group does NOT exist
    Group.objects.filter(name="Read Only").delete()

    # Create a superuser who will receive the email
    admin = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="x"
    )

    # Patch send_mail so we can assert it was called
    with patch("app_accounts.models.signals.send_mail") as mock_send:
        user = User.objects.create_user(username="testuser", email="test@example.com")

        # Signal is automatically triggered by post_save
        # Now assert send_mail was called
        assert mock_send.called
        args, kwargs = mock_send.call_args
        assert "Missing Database Group Notification" in args[0]
        assert admin.email in args[3]


@pytest.mark.django_db
def test_save_user_profile_no_profile_triggers_debug_branch(caplog):
    from django.db.models.signals import post_save
    from app_accounts.models.signals import create_user_profile, save_user_profile

    # Disconnect the profile-creation signal
    post_save.disconnect(create_user_profile, sender=User)

    # Create a user WITHOUT auto-created profile
    user = User.objects.create(username="noprof", email="x@example.com")

    # Confirm no profile exists
    assert not hasattr(user, "profile")

    with caplog.at_level("DEBUG"):
        save_user_profile(User, user)

    assert "profile not saved" in caplog.text

    # Reconnect the signal so other tests are unaffected
    post_save.connect(create_user_profile, sender=User)



@pytest.mark.django_db
def test_create_user_profile_missing_group_no_admins_skips_email():
    # Ensure the "Read Only" group does NOT exist
    Group.objects.filter(name="Read Only").delete()

    # Ensure NO superusers exist
    User.objects.filter(is_superuser=True).delete()

    with patch("app_accounts.models.signals.send_mail") as mock_send:
        User.objects.create_user(username="testuser", email="x@example.com")

        # send_mail should NOT be called
        mock_send.assert_not_called()



@pytest.mark.django_db
def test_create_user_profile_created_false_does_nothing():
    # Create a user normally (created=True)
    user = User.objects.create_user(username="u1", email="u1@example.com")

    # Patch Profile.objects.create to ensure it is NOT called
    with patch("app_accounts.models.signals.Profile.objects.create") as mock_create:
        # Manually call the signal with created=False
        create_user_profile(User, user, created=False)

        mock_create.assert_not_called()
