#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_ip.py
test_ip
/srv/django/MikesLists_dev/app_core/tests/utils/test_ip.py





"""
__version__ = "0.1.0.000026-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 22:52:37"
###############################################################################


import pytest
from types import SimpleNamespace

from app_core.utils.ip import (
    get_client_ip,
    is_ip_in_list,
    is_ip_allowed_for_admin,
    is_local_ip,
    is_private_ip,
)


def make_request(meta):
    return SimpleNamespace(META=meta)


# -----------------------------
# get_client_ip
# -----------------------------

def test_get_client_ip_from_xff_single():
    req = make_request({"HTTP_X_FORWARDED_FOR": "1.2.3.4"})
    assert get_client_ip(req) == "1.2.3.4"


def test_get_client_ip_from_xff_multiple():
    req = make_request({"HTTP_X_FORWARDED_FOR": "1.2.3.4, 5.6.7.8"})
    assert get_client_ip(req) == "1.2.3.4"


def test_get_client_ip_from_remote_addr():
    req = make_request({"REMOTE_ADDR": "9.9.9.9"})
    assert get_client_ip(req) == "9.9.9.9"


def test_get_client_ip_none():
    req = make_request({})
    assert get_client_ip(req) is None


# -----------------------------
# ip_in_list
# -----------------------------

def test_ip_in_list_exact_match():
    assert is_ip_in_list("192.168.1.10", ["192.168.1.10"]) is True


def test_ip_in_list_prefix_match():
    assert is_ip_in_list("192.168.1.55", ["192.168.1."]) is True


def test_ip_in_list_no_match():
    assert is_ip_in_list("10.0.0.1", ["192.168."]) is False


def test_ip_in_list_none_ip():
    assert is_ip_in_list(None, ["192.168."]) is False


# -----------------------------
# ip_allowed_for_admin
# -----------------------------

def test_ip_allowed_for_admin_true():
    assert is_ip_allowed_for_admin("192.168.1.10", ["192.168.1."]) is True


def test_ip_allowed_for_admin_false():
    assert is_ip_allowed_for_admin("10.0.0.1", ["192.168."]) is False


def test_ip_allowed_for_admin_no_ranges():
    assert is_ip_allowed_for_admin("1.2.3.4", None) is False


# -----------------------------
# is_local_ip
# -----------------------------

def test_is_local_ip_true():
    assert is_local_ip("127.0.0.1") is True
    assert is_local_ip("192.168.1.10") is True
    assert is_local_ip("10.0.0.5") is True
    assert is_local_ip("localhost") is True


def test_is_local_ip_false():
    assert is_local_ip("8.8.8.8") is False


def test_is_local_ip_none():
    assert is_local_ip(None) is False


# -----------------------------
# is_private_ip
# -----------------------------

def test_is_private_ip_true():
    assert is_private_ip("192.168.1.10") is True
    assert is_private_ip("10.0.0.1") is True


def test_is_private_ip_false():
    assert is_private_ip("8.8.8.8") is False


def test_is_private_ip_invalid():
    assert is_private_ip("not_an_ip") is False


def test_is_private_ip_none():
    assert is_private_ip(None) is False
