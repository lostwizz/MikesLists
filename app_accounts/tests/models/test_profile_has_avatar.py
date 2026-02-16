#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_profile_has_avatar.py

Test for the has_avatar property to achieve 100% coverage on profile.py
"""
###############################################################################

import pytest
from django.contrib.auth.models import User
from app_accounts.models.profile import Profile


@pytest.mark.django_db
def test_has_avatar_returns_true_when_avatar_exists():
    """Test that has_avatar returns True when avatar_blob is set"""
    user = User.objects.create_user(username="testuser", password="x")
    profile = user.profile

    # Set avatar_blob to some data
    profile.avatar_blob = b"fake image data"
    profile.save()

    assert profile.has_avatar is True


@pytest.mark.django_db
def test_has_avatar_returns_false_when_no_avatar():
    """Test that has_avatar returns False when avatar_blob is None"""
    user = User.objects.create_user(username="testuser", password="x")
    profile = user.profile

    # Ensure no avatar
    profile.avatar_blob = None
    profile.save()

    assert profile.has_avatar is False


@pytest.mark.django_db
def test_has_avatar_returns_false_for_empty_bytes():
    """Test that has_avatar returns False for empty bytes"""
    user = User.objects.create_user(username="testuser", password="x")
    profile = user.profile

    # Set to empty bytes
    profile.avatar_blob = b""
    profile.save()

    # Empty bytes should evaluate to False
    assert profile.has_avatar is False
