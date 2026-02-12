# -*- coding: utf-8 -*-
###############################################################################
r"""
net.py
app_core.utils.net
/srv/django/MikesLists_dev/app_core/utils/net.py

You want:
• 	 → Who is the client?
• 	 → Is the network healthy?
Two different concerns


Network connectivity helpers.

This module focuses on *connectivity* (reachability, ports, DNS, HTTP),
not IP parsing or request metadata. Anything about client IPs belongs
in app_core/utils/ip.py.
All functions are pure, deterministic, and easy to test.

Network utilities for interface diagnostics, Wi-Fi metrics,
Ethernet speed, DNS/HTTP/port checks, and host identity.

use with : from app_core.utils import net



__version__ = "0.0.0.000084-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-11 20:08:29"
"""
###############################################################################

from __future__ import annotations

import os
import socket
import subprocess
import psutil
import time
# import requests



# ----------------------------------------------------------------------
# ping_host - check that a host is there
# ----------------------------------------------------------------------
def ping_host(host, timeout=1.0):
    """Return True if host resolves and accepts a TCP connection on port 80."""
    try:
        start = time.time()
        socket.gethostbyname(host)
        latency = (time.time() - start) * 1000
        return {"ok": True, "latency_ms": latency}
    except Exception:
        return {"ok": False, "latency_ms": None}


# ----------------------------------------------------------------------
# get_ip_addresses -
# ----------------------------------------------------------------------
def get_ip_addresses():
    """Return dict of interface → list of IPs."""
    try:
        result = {}
        for iface, addrs in psutil.net_if_addrs().items():
            ips = [a.address for a in addrs if a.family == socket.AF_INET]
            result[iface] = ips
        return result
    except Exception:
        return {}


# ----------------------------------------------------------------------
# DNS resolver helper
# ----------------------------------------------------------------------
def resolve_hostname(hostname: str) -> dict:
    """
    Resolve a hostname to an IP address.
    Returns:
        {"ok": bool, "ip": str or None, "error": str or None}
    """
    try:
        ip = socket.gethostbyname(hostname)
        return {"ok": True, "ip": ip, "error": None}
    except Exception as e:
        return {"ok": False, "ip": None, "error": str(e)}


# ----------------------------------------------------------------------
# HTTP check helper
# ----------------------------------------------------------------------
def check_http(url: str, timeout: float = 3.0) -> dict:
    """
    Perform a simple HTTP GET request using curl.
    Returns:
        {"ok": bool, "status": int or None, "error": str or None}
    """
    try:
        out = subprocess.check_output(
            ["curl", "-I", "-m", str(timeout), "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
            text=True
        )
        status = int(out.strip())
        return {"ok": 200 <= status < 400, "status": status, "error": None}
    except Exception as e:
        return {"ok": False, "status": None, "error": str(e)}


# ----------------------------------------------------------------------
# Port check helper
# ----------------------------------------------------------------------
def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    Return True if TCP port is open, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


# ----------------------------------------------------------------------
# Interface IPs
# ----------------------------------------------------------------------
def get_interface_ips() -> dict:
    """
    Return {iface: [ip1, ip2]} using `ip -o -4 addr show`.
    """
    result = {}
    try:
        out = subprocess.check_output(
            ["ip", "-o", "-4", "addr", "show"],
            text=True
        )
        for line in out.splitlines():
            parts = line.split()
            iface = parts[1]
            ip = parts[3].split("/")[0]
            result.setdefault(iface, []).append(ip)
    except Exception:
        pass

    return result


# ----------------------------------------------------------------------
# Wi-Fi info (speed, signal, quality)
# ----------------------------------------------------------------------
def get_wifi_info(iface: str) -> dict:
    """
    Return Wi-Fi link speed, signal strength, quality, frequency, channel,
    channel width, noise floor, SNR.
    """
    info = {
        "speed": None,
        "signal_dbm": None,
        "quality": None,
        "noise_dbm": None,
        "frequency": None,
        "channel": None,
        "width_mhz": None,
        "snr": None,
    }

    # ------------------------------------------------------------
    # 1. Parse /proc/net/wireless
    # ------------------------------------------------------------
    try:
        with open("/proc/net/wireless") as f:
            for line in f:
                if iface in line:
                    parts = line.split()
                    info["quality"] = float(parts[2].replace(".", ""))
                    info["signal_dbm"] = float(parts[3].replace(".", ""))
                    info["noise_dbm"] = float(parts[4].replace(".", ""))
    except Exception:
        pass

    # ------------------------------------------------------------
    # 2. Parse `iw dev wlan0 link`
    # ------------------------------------------------------------
    try:
        out = subprocess.check_output(
            ["iw", "dev", iface, "link"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        for line in out.splitlines():
            line = line.strip()

            if line.startswith("tx bitrate:"):
                info["speed"] = line.split("tx bitrate:")[-1].strip()

            if line.startswith("freq:"):
                freq_mhz = line.split("freq:")[-1].strip()
                if freq_mhz.isdigit():
                    info["frequency"] = int(freq_mhz)

            if "channel width" in line:
                # Example: "channel width: 80 MHz"
                parts = line.split()
                for p in parts:
                    if p.isdigit():
                        info["width_mhz"] = int(p)
                        break

    except Exception:
        pass

    # ------------------------------------------------------------
    # 3. Compute channel number
    # ------------------------------------------------------------
    freq = info["frequency"]
    if freq:
        if 2400 <= freq <= 2500:
            info["channel"] = int((freq - 2407) / 5)
        elif 5000 <= freq <= 5900:
            info["channel"] = int((freq - 5000) / 5)
        elif 5925 <= freq <= 7125:
            info["channel"] = int((freq - 5950) / 5)

    # ------------------------------------------------------------
    # 4. Compute SNR
    # ------------------------------------------------------------
    if info["signal_dbm"] is not None and info["noise_dbm"] is not None:
        info["snr"] = info["signal_dbm"] - info["noise_dbm"]

    return info


# ----------------------------------------------------------------------
# Route metrics
# ----------------------------------------------------------------------
def get_route_metrics() -> dict:
    """
    Return {iface: metric} from `ip route show`.
    """
    metrics = {}
    try:
        out = subprocess.check_output(["ip", "route", "show"], text=True)
        for line in out.splitlines():
            parts = line.split()
            if "dev" in parts:
                iface = parts[parts.index("dev") + 1]
                if "metric" in parts:
                    metric = int(parts[parts.index("metric") + 1])
                else:
                    metric = None
                metrics[iface] = metric
    except Exception:
        pass

    return metrics


# ----------------------------------------------------------------------
# Interface type detection
# ----------------------------------------------------------------------
def detect_interface_type(iface: str) -> str:
    """
    Return "wifi", "ethernet", "loopback", or "other".
    """
    if iface == "lo":
        return "loopback"
    if os.path.isdir(f"/sys/class/net/{iface}/wireless"):
        return "wifi"
    if iface.startswith("eth") or iface.startswith("en"):
        return "ethernet"
    return "other"


# ----------------------------------------------------------------------
# Read sysfs helper
# ----------------------------------------------------------------------
def _read_sysfs(path: str):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return None



# ----------------------------------------------------------------------
# wifi calc the collor and band for the display
# ----------------------------------------------------------------------
def get_wifi_color_and_band(data):
    freq = data.get("frequency")
    signal = data.get("wifi_signal")

    # Determine band + label
    if freq is None:
        band = None
        band_label = None
    elif freq >= 5925:
        band = "6ghz"
        band_label = f"6 GHz ({freq} MHz)"
    elif freq >= 5000:
        band = "5ghz"
        band_label = f"5 GHz ({freq} MHz)"
    else:
        band = "2.4ghz"
        band_label = f"2.4 GHz ({freq} MHz)"

    # Determine color
    if band == "6ghz":
        color = "#ab47bc"   # purple
    elif band == "5ghz":
        color = "#2196f3"   # blue
    else:
        # Strength-based colors for 2.4 GHz
        if signal is None:
            color = "#999"
        elif signal > -55:
            color = "#4caf50"   # green
        elif signal > -70:
            color = "#f9a825"   # yellow
        else:
            color = "#e53935"   # red

    return {
        "band": band,
        "band_label": band_label,
        "color": color,
    }


# ----------------------------------------------------------------------
# Host identity helper
# ----------------------------------------------------------------------
def get_host_identity() -> dict:
    """
    Return hostname and primary IP.
    """
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = None

    return {"hostname": hostname, "ip": ip}





# ----------------------------------------------------------------------
# Main: Detailed interface info
# ----------------------------------------------------------------------
def get_interfaces_detailed() -> dict:
    """
    Return structured interface info:
    {
        iface: {
            "ips": [...],
            "mac": "...",
            "state": "up/down/unknown",
            "carrier": "up/down/unknown",
            "speed": "1000 Mb/s" or None,
            "wifi_quality": 70 or None,
            "metric": int or None,
            "type": "ethernet" | "wifi" | "loopback" | "other",
            "wifi_signal": -48 or None,
        }
    }
    """
    ips = get_interface_ips()
    metrics = get_route_metrics()
    result={}

    for iface, ip_list in ips.items():
        wifi = {}   # <-- define it BEFORE the wifi-only block


        base = f"/sys/class/net/{iface}"

        # MAC address
        mac = _read_sysfs(f"{base}/address")

        # operstate
        state = _read_sysfs(f"{base}/operstate") or "unknown"

        # carrier
        carrier_raw = _read_sysfs(f"{base}/carrier")
        if carrier_raw == "1":
            carrier = "up"
        elif carrier_raw == "0":
            carrier = "down"
        else:
            carrier = "unknown"

        # Ethernet speed
        speed_raw = _read_sysfs(f"{base}/speed")
        if speed_raw and speed_raw.isdigit():
            speed = f"{speed_raw} Mb/s"
        else:
            speed = None

        # Interface type
        iface_type = detect_interface_type(iface)


        # Wi-Fi metrics
        wifi_signal = None
        wifi_quality = None
        wifi_freq = None
        if iface_type == "wifi":
            wifi = get_wifi_info(iface)
            if wifi["speed"]:
                speed = wifi["speed"]
            wifi_signal = wifi["signal_dbm"]
            wifi_quality = wifi["quality"]
            wifi_freq = wifi.get("frequency")


        # Wi-Fi health score
        score = 0

        # RSSI
        if wifi_signal is not None:
            if wifi_signal > -55: score += 40
            elif wifi_signal > -65: score += 30
            elif wifi_signal > -75: score += 20
            else: score += 10

        # SNR
        if wifi.get("snr") is not None:
            snr = wifi["snr"]
            if snr > 30: score += 40
            elif snr > 20: score += 30
            elif snr > 10: score += 20
            else: score += 10

        # Band bonus
        if wifi_freq:
            if wifi_freq >= 5925: score += 15
            elif wifi_freq >= 5000: score += 10
            else: score += 5

        # Normalize
        score = min(100, score)

        # Build iface_data
        iface_data = {
            "ips": ip_list,
            "mac": mac,
            "state": state,
            "carrier": carrier,
            "speed": speed,
            "wifi_signal": wifi_signal,
            "wifi_quality": wifi_quality,
            "metric": metrics.get(iface),
            "type": iface_type,
            "frequency": wifi_freq,
            "channel": wifi.get("channel"),
            "width_mhz": wifi.get("width_mhz"),
            "noise_dbm": wifi.get("noise_dbm"),
            "snr": wifi.get("snr"),
            "wifi_health": score,
        }

        wifi_info = get_wifi_color_and_band(iface_data)
        iface_data["wifi_band"] = wifi_info["band"]
        iface_data["wifi_band_label"] = wifi_info["band_label"]
        iface_data["wifi_color"] = wifi_info["color"]

        result[iface] = iface_data


    # Sort: lo → eth0 → wlan0 → everything else
    return dict(sorted(result.items(), key=lambda x: (x[0] != "lo", x[0])))
