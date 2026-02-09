

import pytest
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(username="u", password="p")


@patch("app_core.views.status.get_user_role")
def test_dashboard_admin(mock_role, client, user):
    mock_role.return_value = "admin"
    client.force_login(user)

    response = client.get(reverse("dashboard"))
    assert b"admin" in response.content.lower()


@patch("app_core.views.status.get_user_role")
def test_dashboard_editor(mock_role, client, user):
    mock_role.return_value = "editor"
    client.force_login(user)

    response = client.get(reverse("dashboard"))
    assert b"editor" in response.content.lower()


@patch("app_core.views.status.get_user_role")
def test_dashboard_readonly(mock_role, client, user):
    mock_role.return_value = "readonly"
    client.force_login(user)

    response = client.get(reverse("dashboard"))
    assert b"read-only" in response.content.lower()
