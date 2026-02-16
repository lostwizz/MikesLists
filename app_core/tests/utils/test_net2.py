import builtins
import socket
import types
from unittest.mock import patch, MagicMock, mock_open


import pytest
import psutil

# from app_core.utils import net
# import app_core.utils as net
import app_core.utils.net as net


from unittest.mock import patch


@patch("app_core.utils.net.detect_interface_type", return_value="ethernet")
@patch("app_core.utils.net.get_route_metrics", return_value={})
@patch(
    "app_core.utils.net.get_interface_ips",
    return_value={
        "eth0": ["1.2.3.4"],
        "eth1": ["5.6.7.8"],
    },
)
@patch("app_core.utils.net._read_sysfs")
def test_iface_details_carrier_up(mock_read, *_):
    mock_read.side_effect = [
        # eth0
        "aa:bb:cc",
        "up",
        "1",
        "1000",
        # eth1
        "dd:ee:ff",
        "up",
        "1",
        "1000",
    ]

    result = net.get_interfaces_detailed()
    iface = result["eth0"]

    assert iface["carrier"] == "up"


@patch("app_core.utils.net.detect_interface_type", return_value="ethernet")
@patch("app_core.utils.net.get_route_metrics", return_value={})
@patch(
    "app_core.utils.net.get_interface_ips",
    return_value={
        "eth0": ["1.2.3.4"],
        "eth1": ["5.6.7.8"],
    },
)
@patch("app_core.utils.net._read_sysfs")
def test_iface_details_carrier_down(mock_read, *_):
    mock_read.side_effect = [
        # eth0
        "aa:bb:cc",
        "up",
        "0",
        "1000",
        # eth1
        "dd:ee:ff",
        "up",
        "1",
        "1000",
    ]

    result = net.get_interfaces_detailed()
    iface = result["eth0"]

    assert iface["carrier"] == "down"


@patch("app_core.utils.net.detect_interface_type", return_value="ethernet")
@patch("app_core.utils.net.get_route_metrics", return_value={})
@patch(
    "app_core.utils.net.get_interface_ips",
    return_value={
        "eth0": ["1.2.3.4"],
        "eth1": ["5.6.7.8"],
    },
)
@patch("app_core.utils.net._read_sysfs")
def test_iface_details_carrier_unknown(mock_read, *_):
    mock_read.side_effect = [
        # eth0
        "aa:bb:cc",
        "up",
        "banana",
        "1000",
        # eth1
        "dd:ee:ff",
        "up",
        "1",
        "1000",
    ]

    result = net.get_interfaces_detailed()
    iface = result["eth0"]

    assert iface["carrier"] == "unknown"


import app_core.utils.net as net
from unittest.mock import patch


@patch("app_core.utils.net.os.listdir", return_value=["wlan0"])
@patch("app_core.utils.net.detect_interface_type", return_value="wifi")
@patch("app_core.utils.net.os.path.isdir", return_value=True)
@patch.object(net, "get_route_metrics", return_value={})
@patch.object(
    net,
    "get_interface_ips",
    return_value={
        "wlan0": ["10.0.0.5"],
    },
)
@patch.object(net, "get_wifi_info")
@patch.object(net, "_read_sysfs")
def test_wifi_block_and_health(mock_read, mock_wifi, *_):
    mock_read.side_effect = [
        "aa:bb:cc",
        "up",
        "1",
        "1000",
    ]

    mock_wifi.return_value = {
        "speed": "300 Mb/s",
        "signal_dbm": -40,
        "quality": 80,
        "frequency": 5180,
        "channel": 36,
        "width_mhz": 80,
        "noise_dbm": -90,
        "snr": 35,
    }

    result = net.get_interfaces_detailed()
    iface = result["wlan0"]

    assert iface["type"] == "wifi"
    assert iface["wifi_signal"] == -40
    assert iface["wifi_quality"] == 80
    assert iface["frequency"] == 5180
    assert iface["channel"] == 36
    assert iface["width_mhz"] == 80
    assert iface["noise_dbm"] == -90
    assert iface["snr"] == 35
    assert iface["speed"] == "300 Mb/s"
    assert iface["wifi_health"] > 80


# @patch("app_core.utils.net.os.listdir", return_value=["wlan0"])
# @patch("app_core.utils.net.os.path.isdir", return_value=True)
# @patch("app_core.utils.net.detect_interface_type", return_value="wifi")
# @patch("app_core.utils.net.get_route_metrics", return_value={})
# @patch("app_core.utils.net.get_interface_ips", return_value={"wlan0": ["10.0.0.5"]})
# @patch("app_core.utils.net._read_sysfs", side_effect=["aa:bb:cc", "up", "1", "1000"])
# @patch("app_core.utils.net.get_wifi_info")
# @pytest.mark.parametrize("wifi_signal,expected", [
#     (-50, 40),
#     (-60, 30),
#     (-70, 20),
#     (-80, 10),
#     (None, 0),
# ])
# def test_rssi_scoring(mock_wifi, mock_read, mock_ips, mock_route, mock_type, mock_isdir, mock_listdir,
#                       wifi_signal, expected):
#     mock_wifi.return_value = {
#         "speed": None,
#         "signal_dbm": wifi_signal,
#         "quality": None,
#         "frequency": None,
#         "snr": None,
#     }

#     result = net.get_interfaces_detailed()
#     # assert result["wlan0"]["wifi_health_score"] == expected
#     assert result["wlan0"]["wifi_health"] == expected


import pytest
import app_core.utils.net as net
from unittest.mock import patch


@pytest.fixture
def wifi_env():
    with patch("app_core.utils.net.os.listdir", return_value=["wlan0"]), patch(
        "app_core.utils.net.os.path.isdir", return_value=True
    ), patch("app_core.utils.net.detect_interface_type", return_value="wifi"), patch(
        "app_core.utils.net.get_route_metrics", return_value={}
    ), patch(
        "app_core.utils.net.get_interface_ips", return_value={"wlan0": ["10.0.0.5"]}
    ), patch(
        "app_core.utils.net._read_sysfs", side_effect=["aa:bb:cc", "up", "1", "1000"]
    ), patch(
        "app_core.utils.net.get_wifi_info"
    ) as mock_wifi:

        yield mock_wifi


@pytest.mark.parametrize(
    "wifi_signal,expected",
    [
        (-50, 40),
        (-60, 30),
        (-70, 20),
        (-80, 10),
        (None, 0),
    ],
)
def test_rssi_scoring(wifi_env, wifi_signal, expected):
    wifi_env.return_value = {
        "speed": None,
        "signal_dbm": wifi_signal,
        "quality": None,
        "frequency": None,
        "snr": None,
    }

    result = net.get_interfaces_detailed()
    assert result["wlan0"]["wifi_health"] == expected


@pytest.mark.parametrize(
    "snr,expected",
    [
        (35, 40),
        (25, 30),
        (15, 20),
        (5, 10),
        (None, 0),
    ],
)
def test_snr_scoring(wifi_env, snr, expected):
    wifi_env.return_value = {
        "speed": None,
        "signal_dbm": None,
        "quality": None,
        "frequency": None,
        "snr": snr,
    }

    result = net.get_interfaces_detailed()
    assert result["wlan0"]["wifi_health"] == expected


@pytest.mark.parametrize(
    "freq,expected",
    [
        (6000, 15),  # 6 GHz
        (5200, 10),  # 5 GHz
        (2412, 5),  # 2.4 GHz
        (None, 0),  # no band
    ],
)
def test_band_bonus(wifi_env, freq, expected):
    wifi_env.return_value = {
        "speed": None,
        "signal_dbm": None,
        "quality": None,
        "frequency": freq,
        "snr": None,
    }

    result = net.get_interfaces_detailed()
    assert result["wlan0"]["wifi_health"] == expected
