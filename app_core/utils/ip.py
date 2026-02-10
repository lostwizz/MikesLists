#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
ip.py
app_core.utils.ip
/srv/django/MikesLists_dev/app_core/utils/ip.py

You want:
• 	 → Who is the client?
• 	 → Is the network healthy?
Two different concerns

IP address utility helpers for Django request objects.

These helpers provide safe extraction of client IPs, private‑IP checks,
and admin‑IP allow‑listing.



"""
__version__ = "0.0.0.000051-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-09 19:23:49"
###############################################################################


from typing import Any, Iterable
import ipaddress


# -----------------------------------------------------------------
def get_client_ip(request: Any) -> str | None:
    """
    Extract the real client IP from a Django request.

    Handles:
    - Direct connections (REMOTE_ADDR)
    - Reverse proxies / load balancers (X‑Forwarded‑For)
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # X‑Forwarded‑For may contain multiple IPs

        # s =  xff.split(",")[0].strip()
        # logger.tracea(f"{s=}")
        return xff.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


# -----------------------------------------------------------------
def is_ip_in_list(ip: str | None, allowed: Iterable[str]) -> bool:
    """
    Check whether an IP matches any entry in an allowed list.

    Supports:
    - Exact matches
    - Prefix matches (e.g., "192.168.1.")
    """
    if not ip:
        return False

    for entry in allowed:
        # CIDR support
        if "/" in entry:
            try:
                if ipaddress.ip_address(ip) in ipaddress.ip_network(
                    entry, strict=False
                ):
                    return True
            except ValueError:
                continue

        # Exact or prefix match
        if ip == entry or ip.startswith(entry):
            return True

    return False


# -----------------------------------------------------------------
def is_ip_allowed_for_admin(
    ip: str | None, allowed_ranges: Iterable[str] | None = None
) -> bool:
    """
    Determine whether an IP is allowed to access admin‑only features.

    This is a thin wrapper around is_ip_in_list().
    """
    if not allowed_ranges:
        return False
    return is_ip_in_list(ip, allowed_ranges)


# -----------------------------------------------------------------
def is_local_ip(ip: str | None) -> bool:
    """
    Check whether an IP is a typical local‑network address.
    """
    if not ip:
        return False

    return (
        ip.startswith("127.")
        or ip.startswith("192.168.")
        or ip.startswith("10.")
        or ip == "localhost"
    )


# -----------------------------------------------------------------
def is_private_ip(ip: str | None) -> bool:
    """
    Use Python's ipaddress module to determine whether an IP is private.
    """
    if not ip:
        return False

    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False






# -----------------------------------------------------------------
