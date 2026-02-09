#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
status_service.py
app_core.services.status_service
/srv/django/MikesLists_dev/app_core/services/status_service.py






"""
__version__ = "0.1.0.000029-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 21:57:36"
###############################################################################


from dataclasses import dataclass, asdict
import sys
import subprocess
import django
from django.db import connections
from django.db.utils import OperationalError

from app_core.utils.shell import run
from app_core.utils.env import get_env


@dataclass
class CheckResult:
    name: str
    status: str
    message: str


def collect_checks() -> list[CheckResult]:
    checks: list[CheckResult] = []

    checks.append(CheckResult("Environment", "ok", get_env()))
    checks.append(CheckResult("Python version", "ok", ".".join(map(str, sys.version_info[:3]))))
    checks.append(CheckResult("Django version", "ok", django.get_version()))

    try:
        connections["default"].cursor()
        checks.append(CheckResult("Database connectivity", "ok", "OK"))
    except OperationalError as e:
        checks.append(CheckResult("Database connectivity", "fail", str(e)))

    result = run(f"{sys.executable} manage.py showmigrations --plan")
    if result.returncode == 0:
        pending = any("[ ]" in line for line in result.stdout.splitlines())
        status = "warn" if pending else "ok"
        msg = "Pending migrations exist" if pending else "All migrations applied"
        checks.append(CheckResult("Migrations", status, msg))
    else:
        checks.append(CheckResult("Migrations", "fail", result.stderr.strip()))

    disk = run('df -h / | awk \'NR==2 {print $5 " used (" $4 " free)"}\'')
    if disk.returncode == 0:
        checks.append(CheckResult("Disk on /", "ok", disk.stdout.strip()))

    load = run("cut -d' ' -f1-3 /proc/loadavg")
    if load.returncode == 0:
        checks.append(CheckResult("Load average", "ok", load.stdout.strip()))

    mem = run('free -h | awk \'NR==2 {print $3 " used / " $2 " total"}\'')
    if mem.returncode == 0:
        checks.append(CheckResult("Memory", "ok", mem.stdout.strip()))

    return checks
