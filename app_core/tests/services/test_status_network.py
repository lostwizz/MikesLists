import pytest
from unittest.mock import patch, MagicMock

from app_core.services import status_service


# -----------------------------
# network_diagnostics()
# -----------------------------
@patch("app_core.utils.net.resolve_hostname")
@patch("app_core.utils.net.check_http")
@patch("app_core.utils.net.check_port")
def test_network_diagnostics(
    mock_port, mock_http, mock_resolve
):
    mock_resolve.return_value = {"ok": True, "ip": "1.1.1.1", "error": None}
    mock_http.return_value = {"ok": True, "status": 200, "error": None}
    mock_port.return_value = True

    result = status_service.network_diagnostics()

    assert "dns_google" in result
    assert "http_example" in result
    assert "port_local_80" in result

    assert result["dns_google"]["details"]["ip"] == "1.1.1.1"
    assert result["http_example"]["details"]["status"] == 200
    assert result["port_local_80"]["details"]["ok"] is True


# -----------------------------
# get_status() integration
# -----------------------------
@patch("app_core.services.status_service.network_diagnostics")
def test_get_status_includes_network(mock_net):
    mock_net.return_value = {"fake": "data"}

    result = status_service.get_status()

    assert "network" in result
    assert result["network"] == {"fake": "data"}
