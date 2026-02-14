import types
import pytest
from app_core.utils import ip as iputils


def make_request(meta):
    r = types.SimpleNamespace()
    r.META = meta
    return r


# ---------------------------------------------------------
def test_get_client_ip_from_xff():
    req = make_request({"HTTP_X_FORWARDED_FOR": "1.2.3.4, 5.6.7.8"})
    assert iputils.get_client_ip(req) == "1.2.3.4"


def test_get_client_ip_from_remote_addr():
    req = make_request({"REMOTE_ADDR": "9.9.9.9"})
    assert iputils.get_client_ip(req) == "9.9.9.9"


# ---------------------------------------------------------
def test_is_ip_in_list_none_ip():
    assert iputils.is_ip_in_list(None, ["127.0.0.1"]) is False


def test_is_ip_in_list_exact_match():
    assert iputils.is_ip_in_list("10.0.0.1", ["10.0.0.1"]) is True


def test_is_ip_in_list_prefix_match():
    assert iputils.is_ip_in_list("192.168.1.55", ["192.168.1."]) is True


def test_is_ip_in_list_cidr_match():
    assert iputils.is_ip_in_list("192.168.1.10", ["192.168.1.0/24"]) is True


def test_is_ip_in_list_cidr_malformed_with_slash():
    # Contains "/" so it enters the CIDR block, but is invalid → triggers ValueError
    assert iputils.is_ip_in_list("1.2.3.4", ["10.0.0.0/banana"]) is False


def test_is_ip_in_list_no_match():
    assert iputils.is_ip_in_list("8.8.8.8", ["10.", "192.168."]) is False


# ---------------------------------------------------------
def test_is_ip_allowed_for_admin_none_list():
    assert iputils.is_ip_allowed_for_admin("1.2.3.4", None) is False


def test_is_ip_allowed_for_admin_delegates():
    assert iputils.is_ip_allowed_for_admin("127.0.0.1", ["127."]) is True


# ---------------------------------------------------------
def test_is_local_ip_cases():
    assert iputils.is_local_ip(None) is False
    assert iputils.is_local_ip("127.0.0.1") is True
    assert iputils.is_local_ip("192.168.0.5") is True
    assert iputils.is_local_ip("10.1.2.3") is True
    assert iputils.is_local_ip("localhost") is True
    assert iputils.is_local_ip("8.8.8.8") is False


# ---------------------------------------------------------
def test_is_private_ip():
    assert iputils.is_private_ip(None) is False
    assert iputils.is_private_ip("192.168.1.1") is True
    assert iputils.is_private_ip("8.8.8.8") is False
    assert iputils.is_private_ip("not-an-ip") is False



def test_is_ip_in_list_cidr_malformed_with_slash():
    # Contains "/" so it enters the CIDR block, but is invalid → triggers ValueError
    assert iputils.is_ip_in_list("1.2.3.4", ["10.0.0.0/banana"]) is False


def test_is_ip_in_list_cidr_valid_but_nonmatching_then_prefix_matches():
    # CIDR is valid but does NOT match the IP → falls through to prefix match
    assert iputils.is_ip_in_list("10.1.2.3", ["10.0.0.0/24", "10."]) is True
