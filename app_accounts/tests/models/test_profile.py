#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import base64
from django.contrib.auth.models import User
from app_accounts.models.profile import Profile


@pytest.mark.django_db
def test_profile_email_property():
    user = User.objects.create_user(username="mike", email="mike@example.com")
    profile = user.profile

    assert profile.email == "mike@example.com"


@pytest.mark.django_db
def test_profile_str_method():
    user = User.objects.create_user(username="mike")
    profile = user.profile

    assert str(profile) == "mike's Profile"


@pytest.mark.django_db
def test_get_avatar_base64_returns_none_when_no_blob():
    user = User.objects.create_user(username="mike")
    profile = user.profile

    assert profile.get_avatar_base64() is None


@pytest.mark.django_db
def test_get_avatar_base64_valid_blob():
    user = User.objects.create_user(username="mike")
    profile = user.profile

    raw_bytes = b"test-bytes"
    profile.avatar_blob = raw_bytes
    profile.avatar_mimetype = "image/png"

    expected = base64.b64encode(raw_bytes).decode("utf-8")
    result = profile.get_avatar_base64()

    assert result == f"data:image/png;base64,{expected}"


@pytest.mark.django_db
def test_get_avatar_base64_exception_returns_none(monkeypatch):
    user = User.objects.create_user(username="mike")
    profile = user.profile

    profile.avatar_blob = b"abc"

    # Force base64.b64encode to raise an exception
    def bad_encode(_):
        raise ValueError("boom")

    monkeypatch.setattr("base64.b64encode", bad_encode)

    assert profile.get_avatar_base64() is None
