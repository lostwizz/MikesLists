import builtins
import socket
import types
from unittest.mock import patch, MagicMock, mock_open


import pytest
import psutil

# from app_core.utils import net
# import app_core.utils as net
import app_core.utils.net as net




# ----------------------------------------------------------------------
# ping_host
# ----------------------------------------------------------------------
@patch("socket.gethostbyname")
@patch("time.time", side_effect=[100.0, 100.01])
def test_ping_host_success(mock_time, mock_gethost):
    mock_gethost.return_value = "1.2.3.4"

    result = net.ping_host("example.com")

    assert result["ok"] is True
    assert isinstance(result["latency_ms"], float)
    assert 0 < result["latency_ms"] < 100


@patch("socket.gethostbyname", side_effect=Exception("dns fail"))
def test_ping_host_failure(mock_gethost):
    result = net.ping_host("example.com")

    assert result["ok"] is False
    assert result["latency_ms"] is None


# ----------------------------------------------------------------------
# get_ip_addresses
# ----------------------------------------------------------------------
@patch.object(psutil, "net_if_addrs")
def test_get_ip_addresses_success(mock_net_if_addrs):
    addr1 = types.SimpleNamespace(family=socket.AF_INET, address="192.168.1.10")
    addr2 = types.SimpleNamespace(family=socket.AF_INET6, address="::1")
    mock_net_if_addrs.return_value = {"eth0": [addr1, addr2]}

    result = net.get_ip_addresses()

    assert result == {"eth0": ["192.168.1.10"]}


@patch.object(psutil, "net_if_addrs", side_effect=Exception("boom"))
def test_get_ip_addresses_failure(mock_net_if_addrs):
    result = net.get_ip_addresses()
    assert result == {}


# ----------------------------------------------------------------------
# resolve_hostname
# ----------------------------------------------------------------------
@patch("socket.gethostbyname")
def test_resolve_hostname_success(mock_gethost):
    mock_gethost.return_value = "1.2.3.4"

    result = net.resolve_hostname("example.com")

    assert result["ok"] is True
    assert result["ip"] == "1.2.3.4"
    assert result["error"] is None


@patch("socket.gethostbyname", side_effect=Exception("dns error"))
def test_resolve_hostname_failure(mock_gethost):
    result = net.resolve_hostname("example.com")

    assert result["ok"] is False
    assert result["ip"] is None
    assert "dns error" in result["error"]


# ----------------------------------------------------------------------
# check_http
# ----------------------------------------------------------------------
@patch("subprocess.check_output")
def test_check_http_success_2xx(mock_check_output):
    mock_check_output.return_value = "200"

    result = net.check_http("http://example.com")

    assert result["ok"] is True
    assert result["status"] == 200
    assert result["error"] is None


@patch("subprocess.check_output")
def test_check_http_success_3xx(mock_check_output):
    mock_check_output.return_value = "302"

    result = net.check_http("http://example.com")

    assert result["ok"] is True
    assert result["status"] == 302
    assert result["error"] is None


@patch("subprocess.check_output")
def test_check_http_non_ok_status(mock_check_output):
    mock_check_output.return_value = "500"

    result = net.check_http("http://example.com")

    assert result["ok"] is False
    assert result["status"] == 500
    assert result["error"] is None


@patch("subprocess.check_output", side_effect=Exception("curl fail"))
def test_check_http_failure(mock_check_output):
    result = net.check_http("http://example.com")

    assert result["ok"] is False
    assert result["status"] is None
    assert "curl fail" in result["error"]


# ----------------------------------------------------------------------
# check_port
# ----------------------------------------------------------------------
@patch("socket.create_connection")
def test_check_port_open(mock_create_connection):
    mock_conn = MagicMock()
    mock_create_connection.return_value = mock_conn

    assert net.check_port("127.0.0.1", 80) is True
    mock_create_connection.assert_called_once()


@patch("socket.create_connection", side_effect=Exception("conn fail"))
def test_check_port_closed(mock_create_connection):
    assert net.check_port("127.0.0.1", 80) is False


# ----------------------------------------------------------------------
# get_interface_ips
# ----------------------------------------------------------------------
@patch("subprocess.check_output")
def test_get_interface_ips_success(mock_check_output):
    mock_check_output.return_value = (
        "1: lo    inet 127.0.0.1/8 brd 127.255.255.255 scope host lo\n"
        "2: eth0  inet 192.168.1.10/24 brd 192.168.1.255 scope global eth0\n"
    )

    result = net.get_interface_ips()

    assert result["lo"] == ["127.0.0.1"]
    assert result["eth0"] == ["192.168.1.10"]


@patch("subprocess.check_output", side_effect=Exception("ip fail"))
def test_get_interface_ips_failure(mock_check_output):
    result = net.get_interface_ips()
    assert result == {}


# ----------------------------------------------------------------------
# get_wifi_info
# ----------------------------------------------------------------------
@patch("subprocess.check_output")
@patch.object(
    builtins,
    "open",
    new_callable=mock_open,
    read_data="""
Inter-| sta-|   Quality        |   Discarded packets               | Missed | WE
 face | tus | link level noise |  nwid  crypt   frag  retry   misc | beacon | 22
  wlan0: 0000   54.  -40.  -90.        0      0      0      0      0        0
""",
)
def test_get_wifi_info_full(mock_file, mock_check_output):
    mock_check_output.return_value = """
Connected to aa:bb:cc:dd:ee:ff (on wlan0)
        SSID: MyWifi
        freq: 2412
        tx bitrate: 300.0 MBit/s
        channel width: 80 MHz
"""

    info = net.get_wifi_info("wlan0")

    assert info["quality"] == 54.0
    assert info["signal_dbm"] == -40.0
    assert info["noise_dbm"] == -90.0
    assert info["frequency"] == 2412
    assert info["channel"] == int((2412 - 2407) / 5)
    assert info["speed"] == "300.0 MBit/s"
    assert info["width_mhz"] == 80
    assert info["snr"] == info["signal_dbm"] - info["noise_dbm"]


@patch("subprocess.check_output", side_effect=Exception("iw fail"))
@patch.object(builtins, "open", side_effect=Exception("no wireless"))
def test_get_wifi_info_no_data(mock_file, mock_check_output):
    info = net.get_wifi_info("wlan0")
    assert all(v is None for v in info.values())


# ----------------------------------------------------------------------
# get_route_metrics
# ----------------------------------------------------------------------
@patch("subprocess.check_output")
def test_get_route_metrics_success(mock_check_output):
    mock_check_output.return_value = """
default via 192.168.1.1 dev eth0 proto dhcp metric 100
10.0.0.0/24 dev eth1 proto kernel scope link src 10.0.0.2
"""

    metrics = net.get_route_metrics()

    assert metrics["eth0"] == 100
    assert metrics["eth1"] is None


@patch("subprocess.check_output", side_effect=Exception("route fail"))
def test_get_route_metrics_failure(mock_check_output):
    metrics = net.get_route_metrics()
    assert metrics == {}


# ----------------------------------------------------------------------
# detect_interface_type
# ----------------------------------------------------------------------
@patch("os.path.isdir")
def test_detect_interface_type_loopback(mock_isdir):
    assert net.detect_interface_type("lo") == "loopback"


@patch("os.path.isdir", return_value=True)
def test_detect_interface_type_wifi(mock_isdir):
    assert net.detect_interface_type("wlan0") == "wifi"
    mock_isdir.assert_called_once()


@patch("os.path.isdir", return_value=False)
def test_detect_interface_type_ethernet(mock_isdir):
    assert net.detect_interface_type("eth0") == "ethernet"
    assert net.detect_interface_type("enp3s0") == "ethernet"


@patch("os.path.isdir", return_value=False)
def test_detect_interface_type_other(mock_isdir):
    assert net.detect_interface_type("br0") == "other"


# ----------------------------------------------------------------------
# _read_sysfs
# ----------------------------------------------------------------------
@patch.object(builtins, "open", new_callable=mock_open, read_data="123\n")
def test_read_sysfs_success(mock_file):
    result = net._read_sysfs("/sys/class/net/eth0/speed")
    assert result == "123"


@patch.object(builtins, "open", side_effect=Exception("no file"))
def test_read_sysfs_failure(mock_file):
    result = net._read_sysfs("/sys/class/net/eth0/speed")
    assert result is None


# ----------------------------------------------------------------------
# get_wifi_color_and_band
# ----------------------------------------------------------------------
def test_get_wifi_color_and_band_no_freq():
    data = {"frequency": None, "wifi_signal": None}
    info = net.get_wifi_color_and_band(data)

    assert info["band"] is None
    assert info["band_label"] is None
    assert info["color"] == "#999"


def test_get_wifi_color_and_band_24ghz_signal_buckets():
    # strong signal
    data = {"frequency": 2412, "wifi_signal": -50}
    info = net.get_wifi_color_and_band(data)
    assert info["band"] == "2.4ghz"
    assert info["color"] == "#4caf50"

    # medium
    data = {"frequency": 2412, "wifi_signal": -60}
    info = net.get_wifi_color_and_band(data)
    assert info["color"] == "#f9a825"

    # weak
    data = {"frequency": 2412, "wifi_signal": -80}
    info = net.get_wifi_color_and_band(data)
    assert info["color"] == "#e53935"


def test_get_wifi_color_and_band_5ghz_and_6ghz():
    data = {"frequency": 5200, "wifi_signal": -60}
    info = net.get_wifi_color_and_band(data)
    assert info["band"] == "5ghz"
    assert "5 GHz" in info["band_label"]
    assert info["color"] == "#2196f3"

    data = {"frequency": 6000, "wifi_signal": -60}
    info = net.get_wifi_color_and_band(data)
    assert info["band"] == "6ghz"
    assert "6 GHz" in info["band_label"]
    assert info["color"] == "#ab47bc"


# ----------------------------------------------------------------------
# get_host_identity
# ----------------------------------------------------------------------
@patch("socket.gethostname", return_value="my-host")
@patch("socket.gethostbyname", return_value="10.0.0.5")
def test_get_host_identity_success(mock_gethostbyname, mock_gethostname):
    info = net.get_host_identity()

    assert info["hostname"] == "my-host"
    assert info["ip"] == "10.0.0.5"


@patch("socket.gethostname", return_value="my-host")
@patch("socket.gethostbyname", side_effect=Exception("dns fail"))
def test_get_host_identity_failure(mock_gethostbyname, mock_gethostname):
    info = net.get_host_identity()

    assert info["hostname"] == "my-host"
    assert info["ip"] is None


# ----------------------------------------------------------------------
# get_interfaces_detailed
# ----------------------------------------------------------------------
@patch("app_core.utils.net.get_wifi_color_and_band")
@patch("app_core.utils.net.get_wifi_info")
@patch("app_core.utils.net.detect_interface_type")
@patch("app_core.utils.net._read_sysfs")
@patch("app_core.utils.net.get_route_metrics")
@patch("app_core.utils.net.get_interface_ips")
def test_get_interfaces_detailed_wifi_and_eth(
    mock_get_interface_ips,
    mock_get_route_metrics,
    mock_read_sysfs,
    mock_detect_type,
    mock_get_wifi_info,
    mock_get_wifi_color_and_band,
):
    # Interfaces and IPs
    mock_get_interface_ips.return_value = {
        "wlan0": ["192.168.1.10"],
        "eth0": ["10.0.0.2"],
    }

    # Route metrics
    mock_get_route_metrics.return_value = {
        "wlan0": 100,
        "eth0": 50,
    }

    # sysfs reads: address, operstate, carrier, speed
    def read_sysfs_side_effect(path):
        if "wlan0/address" in path:
            return "aa:bb:cc:dd:ee:ff"
        if "wlan0/operstate" in path:
            return "up"
        if "wlan0/carrier" in path:
            return "1"
        if "wlan0/speed" in path:
            return None
        if "eth0/address" in path:
            return "11:22:33:44:55:66"
        if "eth0/operstate" in path:
            return "down"
        if "eth0/carrier" in path:
            return "0"
        if "eth0/speed" in path:
            return "1000"
        return None

    mock_read_sysfs.side_effect = read_sysfs_side_effect

    # interface types
    def detect_type_side_effect(iface):
        if iface == "wlan0":
            return "wifi"
        if iface == "eth0":
            return "ethernet"
        return "other"

    mock_detect_type.side_effect = detect_type_side_effect

    # wifi info for wlan0
    mock_get_wifi_info.return_value = {
        "speed": "300.0 MBit/s",
        "signal_dbm": -50,
        "quality": 60,
        "noise_dbm": -85,
        "frequency": 2412,
        "channel": 1,
        "width_mhz": 40,
        "snr": 35,
    }

    # wifi color/band
    mock_get_wifi_color_and_band.side_effect = lambda data: {
        "band": "2.4ghz",
        "band_label": "2.4 GHz (2412 MHz)",
        "color": "#4caf50",
    }

    result = net.get_interfaces_detailed()

    # wlan0: wifi, speed overridden by wifi, health computed
    wlan = result["wlan0"]
    assert wlan["ips"] == ["192.168.1.10"]
    assert wlan["mac"] == "aa:bb:cc:dd:ee:ff"
    assert wlan["state"] == "up"
    assert wlan["carrier"] == "up"
    assert wlan["speed"] == "300.0 MBit/s"
    assert wlan["wifi_signal"] == -50
    assert wlan["wifi_quality"] == 60
    assert wlan["metric"] == 100
    assert wlan["type"] == "wifi"
    assert wlan["frequency"] == 2412
    assert wlan["channel"] == 1
    assert wlan["width_mhz"] == 40
    assert wlan["noise_dbm"] == -85
    assert wlan["snr"] == 35
    assert wlan["wifi_health"] == 85  # 40 (RSSI) + 40 (SNR) + 5 (2.4 GHz)
    assert wlan["wifi_band"] == "2.4ghz"
    assert "2.4 GHz" in wlan["wifi_band_label"]
    assert wlan["wifi_color"] == "#4caf50"

    # eth0: ethernet, no wifi metrics
    eth = result["eth0"]
    assert eth["ips"] == ["10.0.0.2"]
    assert eth["mac"] == "11:22:33:44:55:66"
    assert eth["state"] == "down"
    assert eth["carrier"] == "down"
    assert eth["speed"] == "1000 Mb/s"
    assert eth["wifi_signal"] is None
    assert eth["wifi_quality"] is None
    assert eth["metric"] == 50
    assert eth["type"] == "ethernet"
    assert eth["frequency"] is None
    assert eth["channel"] is None
    assert eth["width_mhz"] is None
    assert eth["noise_dbm"] is None
    assert eth["snr"] is None
    assert eth["wifi_health"] == 0


@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_freq_non_digit(mock_run):
    mock_run.return_value = "freq: abc\n"
    info = net.get_wifi_info("wlan0")
    # assert "frequency" not in info
    assert info["frequency"] is None




@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_freq_empty(mock_run):
    mock_run.return_value = "freq:\n"
    info = net.get_wifi_info("wlan0")
    # assert "frequency" not in info
    assert info["frequency"] is None



@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_channel_width_no_digits(mock_run):
    mock_run.return_value = "channel width: eighty MHz\n"
    info = net.get_wifi_info("wlan0")
    # assert "width_mhz" not in info
    assert info["width_mhz"] is None



@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_channel_width_empty(mock_run):
    mock_run.return_value = "channel width:\n"
    info = net.get_wifi_info("wlan0")
    # assert "width_mhz" not in info
    assert info["width_mhz"] is None



@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_channel_width_weird(mock_run):
    mock_run.return_value = "channel width: foo bar baz\n"
    info = net.get_wifi_info("wlan0")
    # assert "width_mhz" not in info
    assert info["width_mhz"] is None




@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_no_freq_no_width(mock_run):
    mock_run.return_value = "some unrelated line\n"
    info = net.get_wifi_info("wlan0")
    # assert "frequency" not in info
    assert info["frequency"] is None
    # assert "width_mhz" not in info
    assert info["width_mhz"] is None




@patch("app_core.utils.net.subprocess.check_output", side_effect=Exception("boom"))
def test_wifi_iw_exception(mock_run):
    info = net.get_wifi_info("wlan0")
    # Should not crash, should return empty info dict
    assert isinstance(info, dict)


@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_channel_calc_24ghz(mock_run):
    mock_run.return_value = "freq: 2412\n"
    info = net.get_wifi_info("wlan0")
    assert info["channel"] == int((2412 - 2407) / 5)

@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_channel_calc_6ghz(mock_run):
    mock_run.return_value = "freq: 5955\n"
    info = net.get_wifi_info("wlan0")
    assert info["channel"] == int((5955 - 5950) / 5)

@patch("app_core.utils.net.subprocess.check_output")
def test_wifi_channel_calc_out_of_range(mock_run):
    mock_run.return_value = "freq: 3000\n"
    info = net.get_wifi_info("wlan0")
    assert info.get("channel") is None
