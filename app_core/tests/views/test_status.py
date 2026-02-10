#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_status.py
test_status
/srv/django/MikesLists_dev/app_core/tests/views/test_status.py





"""
__version__ = "0.1.0.000043-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-09 19:48:44"
###############################################################################


import pytest
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client, RequestFactory, override_settings

from app_core.services.status_service import CheckResult


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff",
        password="pass",
        is_staff=True
    )


@pytest.fixture
def nonstaff_user(db):
    return User.objects.create_user(
        username="user",
        password="pass",
        is_staff=False
    )


# -------------------------------------------------------------------
# ACCESS CONTROL
# -------------------------------------------------------------------

@override_settings(ADMIN_ALLOWED_IP_PREFIXES=["127.0.0.1"])
def test_status_view_forbidden_ip(rf, staff_user):
    request = rf.get("/status")
    request.user = staff_user
    request.META["REMOTE_ADDR"] = "8.8.8.8"

    from app_core.views.status import status_view
    response = status_view(request)

    assert response.status_code == 403


def test_status_view_nonstaff_forbidden(client, nonstaff_user):
    client.login(username="user", password="pass")
    response = client.get(reverse("status_dashboard"))
    assert response.status_code in (302, 403)


def test_status_view_anonymous_redirect(client):
    response = client.get(reverse("status_dashboard"))
    assert response.status_code == 302


# -------------------------------------------------------------------
# JSON MODE
# -------------------------------------------------------------------

@override_settings(ADMIN_ALLOWED_IP_PREFIXES=["127.0.0.1"])
@patch("app_core.views.status.status_service.collect_checks")
def test_status_view_json_mode(mock_checks, rf, staff_user):
    mock_checks.return_value = [
        CheckResult("Test", "ok", "All good")
    ]

    request = rf.get("/status?format=json")
    request.user = staff_user
    request.META["REMOTE_ADDR"] = "127.0.0.1"

    from app_core.views.status import status_view
    response = status_view(request)

    assert response.status_code == 200
    # data = response.json()

    import json
    data = json.loads(response.content.decode("utf-8"))

    assert "env" in data
    assert "checks" in data
    assert data["checks"][0]["name"] == "Test"


# -------------------------------------------------------------------
# HTML MODE
# -------------------------------------------------------------------

@override_settings(ADMIN_ALLOWED_IP_PREFIXES=["127.0.0.1"])
@patch("app_core.views.status.status_service.collect_checks")
def test_status_view_html_mode(mock_checks, client, staff_user):
    mock_checks.return_value = [
        CheckResult("Test", "ok", "All good")
    ]

    client.login(username="staff", password="pass")
    response = client.get(reverse("status_dashboard"))

    assert response.status_code == 200
    assert b"Test" in response.content


# -------------------------------------------------------------------
# RESTART LOGIC
# -------------------------------------------------------------------

@override_settings(
    ADMIN_ALLOWED_IP_PREFIXES=["127.0.0.1"],
    STATUS_ALLOW_RESTART=True,
)
@patch("app_core.views.status.status_service.collect_checks", return_value=[])
@patch("app_core.views.status.restart_allowed", return_value=True)
@patch("app_core.views.status.perform_restart")
def test_status_view_restart_success(mock_restart, mock_allowed, mock_checks, rf, staff_user):
    mock_restart.return_value = (True, "Restart OK")

    request = rf.post("/status")
    request.user = staff_user
    request.META["REMOTE_ADDR"] = "127.0.0.1"

    # print("REMOTE_ADDR =", request.META.get("REMOTE_ADDR"))
    # print("XFF =", request.META.get("HTTP_X_FORWARDED_FOR"))

    from app_core.views.status import status_view
    response = status_view(request)

    assert response.status_code == 200
    assert b"Restart OK" in response.content


@override_settings(
    ADMIN_ALLOWED_IP_PREFIXES=["127.0.0.1"],
    STATUS_ALLOW_RESTART=True,
)
@patch("app_core.views.status.status_service.collect_checks", return_value=[])
@patch("app_core.views.status.restart_allowed", return_value=True)
@patch("app_core.views.status.perform_restart")
def test_status_view_restart_failure(mock_restart, mock_allowed, mock_checks, rf, staff_user):
    mock_restart.return_value = (False, "FAILED: boom")


    request = rf.post("/status")
    request.user = staff_user
    request.META["REMOTE_ADDR"] = "127.0.0.1"

    from app_core.views.status import status_view
    response = status_view(request)

    assert response.status_code == 200
    assert b"FAILED" in response.content
