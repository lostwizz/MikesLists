#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_auth.py
test_auth
/srv/django/MikesLists_dev/app_core/tests/utils/test_auth.py




"""
__version__ = "0.1.0.000024-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 21:37:56"
###############################################################################


import pytest
from app_core.utils.auth import (
    is_authenticated,
    is_staff,
    is_superuser,
    require_staff,
)


class DummyUser:
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)


def test_is_authenticated_true():
    user = DummyUser(is_authenticated=True)
    assert is_authenticated(user) is True


def test_is_authenticated_false():
    user = DummyUser(is_authenticated=False)
    assert is_authenticated(user) is False


def test_is_authenticated_missing_attribute():
    user = DummyUser()
    assert is_authenticated(user) is False


def test_is_staff_true():
    user = DummyUser(is_staff=True)
    assert is_staff(user) is True


def test_is_staff_false():
    user = DummyUser(is_staff=False)
    assert is_staff(user) is False


def test_is_staff_missing_attribute():
    user = DummyUser()
    assert is_staff(user) is False


def test_is_superuser_true():
    user = DummyUser(is_superuser=True)
    assert is_superuser(user) is True


def test_is_superuser_false():
    user = DummyUser(is_superuser=False)
    assert is_superuser(user) is False


def test_is_superuser_missing_attribute():
    user = DummyUser()
    assert is_superuser(user) is False


def test_require_staff_allows_staff():
    user = DummyUser(is_staff=True)
    require_staff(user)  # should not raise


def test_require_staff_raises_for_non_staff():
    user = DummyUser(is_staff=False)
    with pytest.raises(PermissionError):
        require_staff(user)


def test_require_staff_missing_attribute():
    user = DummyUser()
    with pytest.raises(PermissionError):
        require_staff(user)
