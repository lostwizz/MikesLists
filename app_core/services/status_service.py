#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
status_service.py
app_core.services.status_service
/srv/django/MikesLists_dev/app_core/services/status_service.py






"""
__version__ = "0.1.0.000039-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-09 22:03:01"
###############################################################################


from dataclasses import dataclass, asdict
import sys
import time
import subprocess
import django
import socket

from django.db import connections
from django.db.utils import OperationalError

from app_core.utils.shell import run
from app_core.utils.env import get_env
# from app_core.utils import get_client_ip

from app_core.utils import net, ip


# ##############################################################################
# ##############################################################################
@dataclass
class CheckResult:
    name: str
    status: str
    message: str




# -----------------------------------------------------------------
def get_status(request=None):
    """
    Unified status aggregator for both JSON and HTML.
    """
    return {
        "status": "ok",

        # Environment
        "env": get_env(),

        # System checks
        "checks": collect_checks(),

        # Network diagnostics
        "network": network_diagnostics(),

        # Interfaces
        "interfaces": net.get_interfaces_detailed(),

        # Host identity
        "host_identity": net.get_host_identity(),

        # Client identity
        "remote_ip": request.META.get("REMOTE_ADDR") if request else None,
        "client_ip": ip.get_client_ip(request) if request else None,
    }


# -----------------------------------------------------------------
def collect_checks() -> list[CheckResult]:
    checks: list[CheckResult] = []

    checks.append(CheckResult("Environment", "ok", get_env()))
    checks.append(CheckResult("Python version", "ok", ".".join(map(str, sys.version_info[:3]))))
    checks.append(CheckResult("Django version", "ok", django.get_version()))

    # Database connectivity
    try:
        connections["default"].cursor()
        checks.append(CheckResult("Database connectivity", "ok", "OK"))
    except OperationalError as e:
        checks.append(CheckResult("Database connectivity", "fail", str(e)))

    # Migrations
    result = run([sys.executable, "manage.py", "showmigrations", "--plan"])
    if result.returncode == 0:
        pending = any("[ ]" in line for line in result.stdout.splitlines())
        status = "warn" if pending else "ok"
        msg = "Pending migrations exist" if pending else "All migrations applied"
        checks.append(CheckResult("Migrations", status, msg))
    else:
        checks.append(CheckResult("Migrations", "fail", result.stderr.strip()))

    # Disk usage
    disk = run(["df", "-h", "/"])
    if disk.returncode == 0:
        line = disk.stdout.splitlines()[1]
        used = line.split()[4]
        free = line.split()[3]
        checks.append(CheckResult("Disk on /", "ok", f"{used} used ({free} free)"))

    # Load average
    load = run(["cut", "-d", " ", "-f1-3", "/proc/loadavg"])
    if load.returncode == 0:
        checks.append(CheckResult("Load average", "ok", load.stdout.strip()))

    # Memory
    mem = run(["free", "-h"])
    if mem.returncode == 0:
        parts = mem.stdout.splitlines()[1].split()
        used = parts[2]
        total = parts[1]
        checks.append(CheckResult("Memory", "ok", f"{used} used / {total} total"))

    return checks




# -----------------------------------------------------------------
def _emoji(ok: bool) -> str:
    return "🟢" if ok else "🔴"


# -----------------------------------------------------------------
def _measure(fn, *args, **kwargs):
    """Run a function and measure latency in ms."""
    start = time.time()
    result = fn(*args, **kwargs)
    latency = round((time.time() - start) * 1000, 2)
    return result, latency


# -----------------------------------------------------------------
def get_interfaces():
    return net.get_interface_ips()

# -----------------------------------------------------------------
def get_host_identity():
    return net.get_host_identity()

# -----------------------------------------------------------------
def get_client_ip(request):
    return ip.get_client_ip(request)

# -----------------------------------------------------------------
def get_remote_ip(request):
    return request.META.get("REMOTE_ADDR", "unknown")



# -----------------------------------------------------------------
def network_diagnostics():
    results = {}

    # DNS
    dns_result, dns_latency = _measure(net.resolve_hostname, "google.com")
    results["dns_google"] = {
        "ok": dns_result["ok"],
        "emoji": _emoji(dns_result["ok"]),
        "latency_ms": dns_latency,
        "details": dns_result,
    }

    # HTTP
    http_result, http_latency = _measure(net.check_http, "http://example.com")
    results["http_example"] = {
        "ok": http_result["ok"],
        "emoji": _emoji(http_result["ok"]),
        "latency_ms": http_latency,
        "details": http_result,
    }

    # Port check
    port_ok, port_latency = _measure(net.check_port, "127.0.0.1", 80)
    results["port_local_80"] = {
        "ok": port_ok,
        "emoji": _emoji(port_ok),
        "latency_ms": port_latency,
        "details": {
            "host": "127.0.0.1",
            "port": 80,
            "ok": port_ok,
        },
    }

    return results


# def get_client_ip(request):
#     """
#     Return the real client IP, respecting X-Forwarded-For if present.
#     Safe: only trusts the left-most IP.
#     """
#     xff = request.META.get("HTTP_X_FORWARDED_FOR")
#     if xff:
#         # XFF may contain multiple IPs: client, proxy1, proxy2...
#         return xff.split(",")[0].strip()

#     return request.META.get("REMOTE_ADDR", "unknown")
