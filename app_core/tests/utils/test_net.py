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



import types
import app_core.utils.net as net


def test_get_interfaces_detailed_structure(monkeypatch):
    # Fake IPs
    monkeypatch.setattr(
        net,
        "get_interface_ips",
        lambda: {"lo": ["127.0.0.1"], "wlan0": ["10.0.0.9"]},
    )

    # Fake route metrics
    monkeypatch.setattr(
        net,
        "get_route_metrics",
        lambda: {"lo": 0, "wlan0": 600},
    )

    # Fake sysfs reads
    def fake_read_sysfs(path):
        if "lo/operstate" in path:
            return "unknown"
        if "wlan0/operstate" in path:
            return "up"
        if "wlan0/address" in path:
            return "2c:cf:67:6e:9b:37"
        if "wlan0/carrier" in path:
            return "1"
        if "wlan0/speed" in path:
            return "1000"
        return None

    monkeypatch.setattr(net, "_read_sysfs", fake_read_sysfs)

    # Fake type detection
    monkeypatch.setattr(
        net,
        "detect_interface_type",
        lambda iface: "loopback" if iface == "lo" else "wifi",
    )

    # Fake Wi-Fi info
    def fake_wifi_info(iface):
        return {
            "speed": "144.4 MBit/s",
            "signal_dbm": -48.0,
            "quality": 70.0,
            "noise_dbm": -256.0,
        }

    monkeypatch.setattr(net, "get_wifi_info", fake_wifi_info)

    data = net.get_interfaces_detailed()
    assert set(data.keys()) == {"lo", "wlan0"}

    lo = data["lo"]
    assert lo["ips"] == ["127.0.0.1"]
    assert lo["type"] == "loopback"
    assert lo["metric"] == 0

    wlan = data["wlan0"]
    assert wlan["ips"] == ["10.0.0.9"]
    assert wlan["mac"] == "2c:cf:67:6e:9b:37"
    assert wlan["state"] == "up"
    assert wlan["carrier"] == "up"
    assert wlan["speed"] == "144.4 MBit/s"
    assert wlan["wifi_signal"] == -48.0
    assert wlan["wifi_quality"] == 70.0
    assert wlan["metric"] == 600
    assert wlan["type"] == "wifi"


def test_resolve_hostname_ok(monkeypatch):
    def fake_gethostbyname(host):
        assert host == "example.com"
        return "93.184.216.34"

    monkeypatch.setattr(net.socket, "gethostbyname", fake_gethostbyname)
    result = net.resolve_hostname("example.com")
    assert result["ok"] is True
    assert result["ip"] == "93.184.216.34"
    assert result["error"] is None


def test_resolve_hostname_fail(monkeypatch):
    def fake_gethostbyname(host):
        raise OSError("boom")

    monkeypatch.setattr(net.socket, "gethostbyname", fake_gethostbyname)
    result = net.resolve_hostname("bad.host")
    assert result["ok"] is False
    assert result["ip"] is None
    assert "boom" in result["error"]


def test_check_port_open(monkeypatch):
    class DummySocket:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    def fake_create_connection(addr, timeout=1.0):
        assert addr == ("127.0.0.1", 80)
        return DummySocket()

    monkeypatch.setattr(net.socket, "create_connection", fake_create_connection)
    assert net.check_port("127.0.0.1", 80) is True


def test_check_port_closed(monkeypatch):
    def fake_create_connection(addr, timeout=1.0):
        raise OSError("refused")

    monkeypatch.setattr(net.socket, "create_connection", fake_create_connection)
    assert net.check_port("127.0.0.1", 80) is False
