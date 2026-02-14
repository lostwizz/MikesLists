import json
import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.http import HttpResponseForbidden

from app_core.views.status import status, status_view, dashboard


@pytest.fixture
def rf():
    return RequestFactory()


# ---------------------------------------------------------
# 1. Test the simple status() function
# ---------------------------------------------------------
@patch("app_core.views.status.status_service.get_status", return_value={"ok": True})
def test_status_simple(mock_status, rf):
    request = rf.get("/status/")
    response = status(request)
    assert response.status_code == 200
    assert json.loads(response.content) == {"ok": True}


# ---------------------------------------------------------
# 2. Forbidden IP branch
# ---------------------------------------------------------
@patch("app_core.views.status.is_admin_access_allowed", return_value=False)
def test_status_view_forbidden_ip(mock_ip, rf):
    request = rf.get("/status/")
    request.user = MagicMock(is_staff=True)
    response = status_view(request)
    assert isinstance(response, HttpResponseForbidden)
    assert response.status_code == 403


# ---------------------------------------------------------
# 3. JSON mode
# ---------------------------------------------------------
class DummyCheck:
    def __init__(self):
        self.name = "Test"
        self.status = "ok"

@patch("app_core.views.status.is_admin_access_allowed", return_value=True)
@patch("app_core.views.status.status_service.get_status")
@patch("app_core.views.status.get_env", return_value="dev")
def test_status_view_json_mode(mock_env, mock_status, mock_ip, rf):
    mock_status.return_value = {"checks": [DummyCheck()]}

    request = rf.get("/status/?format=json")
    request.user = MagicMock(is_staff=True)

    response = status_view(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert data["env"] == "dev"
    assert data["checks"][0]["name"] == "Test"


# ---------------------------------------------------------
# 4. Restart POST branch
# ---------------------------------------------------------
@patch("app_core.views.status.is_admin_access_allowed", return_value=True)
@patch("app_core.views.status.restart_allowed", return_value=True)
@patch("app_core.views.status.perform_restart", return_value=(True, "Restart OK"))
@patch("app_core.views.status.status_service.get_status", return_value={"checks": []})
def test_status_view_restart(mock_status, mock_restart, mock_allowed, mock_ip, rf):
    request = rf.post("/status/")
    request.user = MagicMock(is_staff=True)

    with patch("app_core.views.status.render") as mock_render:
        status_view(request)
        args, kwargs = mock_render.call_args
        context = args[2]
        assert context["message"] == "Restart OK"


# ---------------------------------------------------------
# 5. HTML mode
# ---------------------------------------------------------
@patch("app_core.views.status.is_admin_access_allowed", return_value=True)
@patch("app_core.views.status.status_service.get_status", return_value={"checks": []})
def test_status_view_html(mock_status, mock_ip, rf):
    request = rf.get("/status/")
    request.user = MagicMock(is_staff=True)

    with patch("app_core.views.status.render") as mock_render:
        status_view(request)
        args, kwargs = mock_render.call_args
        context = args[2]
        assert "checks" in context
