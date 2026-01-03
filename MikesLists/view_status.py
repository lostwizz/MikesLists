# core/views_status.py

import subprocess
from dataclasses import dataclass

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@dataclass
class CheckResult:
    name: str
    status: str  # "ok", "warn", "fail"
    message: str


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def status_view(request: HttpRequest) -> HttpResponse:
    checks = []

    # Example checks – mirror your CLI logic where it makes sense

    # Python / Django
    from django.conf import settings
    import django
    import sys

    checks.append(
        CheckResult(
            name="Python version",
            status="ok",
            message=".".join(map(str, sys.version_info[:3])),
        )
    )
    checks.append(
        CheckResult(
            name="Django version",
            status="ok",
            message=django.get_version(),
        )
    )

    # Database
    from django.db import connections
    from django.db.utils import OperationalError

    db_conn = connections["default"]
    try:
        db_conn.cursor()
        checks.append(CheckResult(name="Database connectivity", status="ok", message="OK"))
    except OperationalError as e:
        checks.append(CheckResult(name="Database connectivity", status="fail", message=str(e)))

    # Migrations
    result = run(f"{sys.executable} manage.py showmigrations --plan")
    if result.returncode == 0:
        pending = any("[ ]" in line for line in result.stdout.splitlines())
        if pending:
            checks.append(CheckResult(name="Migrations", status="warn", message="Pending migrations exist"))
        else:
            checks.append(CheckResult(name="Migrations", status="ok", message="All migrations applied"))
    else:
        checks.append(CheckResult(name="Migrations", status="fail", message=result.stderr.strip()))

    # Gunicorn/nginx status is usually better checked from CLI, but you can query px/ps if needed

    context = {
        "checks": checks,
        "env": getattr(settings, "ENV_NAME", "dev"),
    }
    return render(request, "status/dashboard.html", context)
