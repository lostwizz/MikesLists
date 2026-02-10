import pytest
import socket
import urllib.error
from unittest.mock import patch, MagicMock

from app_core.utils import net


# -----------------------------
# ping_host
# -----------------------------
def test_ping_host_success():
    with patch("socket.create_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value = True
        assert net.ping_host("example.com") is True


def test_ping_host_failure():
    with patch("socket.create_connection", side_effect=OSError("fail")):
        assert net.ping_host("example.com") is False


# -----------------------------
# check_port
# -----------------------------
def test_check_port_success():
    with patch("socket.create_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value = True
        assert net.check_port("localhost", 80) is True


def test_check_port_failure():
    with patch("socket.create_connection", side_effect=OSError("nope")):
        assert net.check_port("localhost", 80) is False


# -----------------------------
# resolve_hostname
# -----------------------------
def test_resolve_hostname_success():
    with patch("socket.gethostbyname", return_value="1.2.3.4"):
        result = net.resolve_hostname("example.com")
        assert result["ok"] is True
        assert result["ip"] == "1.2.3.4"
        assert result["error"] is None


def test_resolve_hostname_failure():
    with patch("socket.gethostbyname", side_effect=Exception("boom")):
        result = net.resolve_hostname("example.com")
        assert result["ok"] is False
        assert result["ip"] is None
        assert "boom" in result["error"]


def test_resolve_hostname_timeout(monkeypatch):
    # Force time.time() to simulate a long delay
    calls = [0, 10]  # start, end
    monkeypatch.setattr(net.time, "time", lambda: calls.pop(0))

    with patch("socket.gethostbyname", return_value="1.2.3.4"):
        result = net.resolve_hostname("example.com", timeout=1.0)
        assert result["ok"] is False
        assert result["ip"] is None
        assert result["error"] == "timeout"


# -----------------------------
# check_http
# -----------------------------
def test_check_http_success():
    mock_resp = MagicMock()
    mock_resp.status = 200

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        result = net.check_http("http://example.com")
        assert result["ok"] is True
        assert result["status"] == 200
        assert result["error"] is None


def test_check_http_http_error():
    exc = urllib.error.HTTPError(
        url="http://example.com",
        code=404,
        msg="Not Found",
        hdrs=None,
        fp=None,
    )

    with patch("urllib.request.urlopen", side_effect=exc):
        result = net.check_http("http://example.com")
        assert result["ok"] is False
        assert result["status"] == 404
        assert "Not Found" in result["error"]


def test_check_http_generic_error():
    with patch("urllib.request.urlopen", side_effect=Exception("boom")):
        result = net.check_http("http://example.com")
        assert result["ok"] is False
        assert result["status"] is None
        assert "boom" in result["error"]


# -----------------------------
# get_ip_addresses
# -----------------------------
def test_get_ip_addresses_success():
    with patch("socket.gethostname", return_value="myhost"):
        with patch("socket.gethostbyname", return_value="1.2.3.4"):
            result = net.get_ip_addresses()
            assert result == {"myhost": "1.2.3.4"}


def test_get_ip_addresses_failure():
    with patch("socket.gethostname", return_value="myhost"):
        with patch("socket.gethostbyname", side_effect=Exception("nope")):
            result = net.get_ip_addresses()
            assert result == {"myhost": None}
