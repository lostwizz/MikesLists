import pytest
from django.urls import reverse
from django.test import RequestFactory

from app_core.views.home import (
    redirect_root_to_dashboard,
    redirect_home_to_dashboard,
    redirect_accounts_to_dashboard,
    redirect_dashboard_to_dashboard,
    catchall_redirect,
    home,
)


@pytest.fixture
def rf():
    return RequestFactory()


def test_redirect_root_to_dashboard(rf):
    request = rf.get("/")
    response = redirect_root_to_dashboard(request)
    assert response.status_code == 302
    assert response.url == reverse("accounts:dashboard")


def test_redirect_home_to_dashboard(rf):
    request = rf.get("/home/")
    response = redirect_home_to_dashboard(request)
    assert response.status_code == 302
    assert response.url == reverse("accounts:dashboard")


def test_redirect_accounts_to_dashboard(rf):
    request = rf.get("/accounts/")
    response = redirect_accounts_to_dashboard(request)
    assert response.status_code == 302
    assert response.url == reverse("accounts:dashboard")


def test_redirect_dashboard_to_dashboard(rf):
    request = rf.get("/dashboard/")
    response = redirect_dashboard_to_dashboard(request)
    assert response.status_code == 302
    assert response.url == reverse("accounts:dashboard")


def test_catchall_redirect(rf):
    request = rf.get("/anything/here/")
    response = catchall_redirect(request, path="anything/here/")
    assert response.status_code == 302
    assert response.url == reverse("accounts:dashboard")


from unittest.mock import patch
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

from app_core.views.home import home


def test_home_view_renders_template(rf, monkeypatch):
    request = rf.get("/home/")
    request.user = AnonymousUser()  # <-- FIX

    # Make get_env deterministic
    monkeypatch.setattr("app_core.views.home.get_env", lambda: "dev")

    response = home(request)

    assert response.status_code == 200
    assert b"dev" in response.content
