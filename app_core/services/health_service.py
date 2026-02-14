#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
health_service.py
health_service
/srv/django/MikesLists_dev/app_core/services/health_service.py


Modernized Health Service
-------------------------

A clean, testable, extensible health check framework.

Features:
- Plugin-style check registry
- Deterministic behavior in TESTING mode
- No Pi-specific hardcoding in core logic
- No subprocess failures blocking tests
- Unified CheckResult model
- Predictable output for frontend dashboards


__version__ = "0.0.1.000080-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-11 22:44:17"
"""
###############################################################################

from __future__ import annotations

import os
import time
import json
import psutil
import shutil
import subprocess
from dataclasses import dataclass, asdict
from typing import Callable, Dict, Any

from django.conf import settings
from django.db import connections
from app_core.logging.logging import logger


# ---------------------------------------------------------------------------
# Core Data Model
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    name: str
    status: str
    message: str = ""
    raw_value: Any = None

    def to_dict(self):
        """Hide raw values in production."""
        if getattr(settings, "TESTING", False) or getattr(settings, "DEBUG", False):
            return asdict(self)
        return {"name": self.name, "status": self.status}


# ---------------------------------------------------------------------------
# Utility Helpers
# ---------------------------------------------------------------------------

def safe_run(func: Callable, *args, **kwargs):
    """Run a function safely, capturing exceptions as fail results."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.exception(f"Health check error in {func.__name__}: {e}")
        return CheckResult(func.__name__, "fail", str(e), None)


def bytes2human(n: int) -> str:
    """Convert bytes to human-readable string."""
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {s: 1 << (i + 1) * 10 for i, s in enumerate(symbols)}
    for s in reversed(symbols):
        if n >= prefix[s]:
            return f"{float(n) / prefix[s]:.1f}{s}"
    return f"{n}B"


# ---------------------------------------------------------------------------
# Check Implementations
# ---------------------------------------------------------------------------

def check_disk() -> CheckResult:
    path = getattr(settings, "HEALTH_CHECK_DISK_PATH", "/")
    total, used, free = shutil.disk_usage(path)
    free_mb = free // (1024 * 1024)
    status = "ok" if free_mb > 100 else "warn"
    return CheckResult("disk", status, f"{bytes2human(free)} free", free)


def check_ram() -> CheckResult:
    mem = psutil.virtual_memory()
    status = "ok" if mem.percent < 85 else "warn"
    return CheckResult("ram", status, f"{mem.percent}%", mem._asdict())


def check_cpu() -> CheckResult:
    cpu = psutil.cpu_percent(interval=0.1)
    status = "ok" if cpu < 90 else "warn"
    return CheckResult("cpu", status, f"{cpu}%", cpu)


def check_temp_sensors() -> CheckResult:
    temps = psutil.sensors_temperatures()
    if not temps:
        return CheckResult("temps", "skip", "no sensors", None)

    # flatten and guard against empty lists
    flat = [t.current for group in temps.values() for t in group]
    if not flat:
        return CheckResult("temps", "skip", "no sensors", None)

    max_temp = max(flat)
    status = "ok" if max_temp <= 80 else "warn"
    return CheckResult("temps", status, f"{max_temp}°C", temps)




def check_zombies() -> CheckResult:
    zombies = [
        p.pid for p in psutil.process_iter(["status"])
        if p.info["status"] == psutil.STATUS_ZOMBIE
    ]
    status = "ok" if not zombies else "warn"
    msg = "no zombies" if not zombies else f"{len(zombies)} zombies"
    return CheckResult("zombies", status, msg, zombies)


def check_sd_latency() -> CheckResult:
    start = time.perf_counter()
    try:
        with open("/tmp/health_test.tmp", "wb") as f:
            f.write(os.urandom(1024))
    except Exception as e:
        return CheckResult("sd_latency", "fail", str(e), None)

    duration = (time.perf_counter() - start) * 1000
    status = "ok" if duration < 100 else "warn"
    return CheckResult("sd_latency", status, f"{duration:.2f}ms", duration)


def check_ping() -> CheckResult:
    if not getattr(settings, "TESTING", False):
        try:
            subprocess.check_call(
                ["ping", "-c", "1", "-W", "1", "8.8.8.8"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return CheckResult("ping", "ok", "reachable", None)
        except Exception as e:
            return CheckResult("ping", "fail", str(e), None)
    return CheckResult("ping", "ok", "test-mode", None)


def check_database() -> CheckResult:
    try:
        conn = connections["default"]
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()[0]
        return CheckResult("database", "ok", f"select 1 = {result}", result)
    except Exception as e:
        return CheckResult("database", "fail", str(e), None)


# ---------------------------------------------------------------------------
# Plugin Registry
# ---------------------------------------------------------------------------

CHECK_REGISTRY: Dict[str, Callable[[], CheckResult]] = {
    "disk": check_disk,
    "ram": check_ram,
    "cpu": check_cpu,
    "temps": check_temp_sensors,
    "zombies": check_zombies,
    "sd_latency": check_sd_latency,
    "ping": check_ping,
    "database": check_database,
}


# ---------------------------------------------------------------------------
# Main Service
# ---------------------------------------------------------------------------

def health_service() -> Dict[str, CheckResult]:
    """
    Run all registered health checks and return a dictionary of results.
    Deterministic in TESTING mode.
    """

    results: Dict[str, CheckResult] = {}

    for name, func in CHECK_REGISTRY.items():
        results[name] = safe_run(func)

    # Remove skipped checks unless in testing
    if not getattr(settings, "TESTING", False):
        results = {k: v for k, v in results.items() if v.status != "skip"}

    return results
