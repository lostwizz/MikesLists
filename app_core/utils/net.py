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



use with : from app_core.utils import net



__version__ = "0.0.0.000031-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-09 19:37:40"
"""
###############################################################################

from __future__ import annotations

import socket
import time
import urllib.request
import urllib.error


# -----------------------------------------------------------------
def ping_host(host: str, timeout: float = 1.0) -> bool:
    """
    Return True if the host is reachable via TCP connect on port 80.

    This is intentionally simple and avoids subprocess calls.
    """
    try:
        conn = socket.create_connection((host, 80), timeout=timeout)
        conn.close()
        return True
    except Exception:
        return False


# -----------------------------------------------------------------
def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    Return True if a TCP port is open.
    """
    try:
        conn = socket.create_connection((host, port), timeout=timeout)
        conn.close()
        return True
    except Exception:
        return False


# -----------------------------------------------------------------
def resolve_hostname(hostname: str, timeout: float = 1.0) -> dict:
    """
    Resolve a hostname to an IP address.

    Returns:
        {
            "ok": bool,
            "ip": str | None,
            "error": str | None,
        }
    """
    start = time.time()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception as exc:
        return {"ok": False, "ip": None, "error": str(exc)}

    elapsed = time.time() - start
    if elapsed > timeout:
        return {"ok": False, "ip": None, "error": "timeout"}

    return {"ok": True, "ip": ip, "error": None}


# -----------------------------------------------------------------
def check_http(url: str, timeout: float = 2.0) -> dict:
    """
    Perform a simple HTTP GET request.

    Returns:
        {
            "ok": bool,
            "status": int | None,
            "error": str | None,
        }
    """
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": resp.status, "error": None}

    except urllib.error.HTTPError as exc:
        # HTTPError includes a status code
        return {"ok": False, "status": exc.code, "error": str(exc)}

    except Exception as exc:
        return {"ok": False, "status": None, "error": str(exc)}


# -----------------------------------------------------------------
def get_ip_addresses() -> dict:
    """
    Return a mapping of network interfaces to IP addresses.

    This is intentionally simple and avoids platform‑specific libraries.
    """
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
        return {hostname: ip}
    except Exception:
        return {hostname: None}


# -----------------------------------------------------------------
def get_local_ip():
    """
    Return the primary LAN IP address (e.g., 10.0.0.x or 192.168.x.x).
    Works even when hostname resolves to 127.0.0.1.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable — no packets are sent
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


# -----------------------------------------------------------------
def get_host_identity():
    return {
        "hostname": socket.gethostname(),
        "ip": get_local_ip(),
    }

# -----------------------------------------------------------------
# def get_host_identity():
#     """Return hostname and primary IP address of this server."""
#     hostname = socket.gethostname()

#     try:
#         ip = socket.gethostbyname(hostname)
#     except Exception:
#         ip = "unknown"

#     return {
#         "hostname": hostname,
#         "ip": ip,
#     }
