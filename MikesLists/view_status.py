import os
import subprocess
import sys
from dataclasses import dataclass, asdict

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render



from django.http import HttpResponseForbidden

ALLOWED_IPS = ["10.0.0.0/24", "127.0.0.1"]

def ip_allowed(request):
    ip = request.META.get("REMOTE_ADDR")
    return ip.startswith("10.0.0.") or ip == "127.0.0.1"



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


def is_staff(user) -> bool:
    return user.is_staff


def collect_checks() -> list[CheckResult]:
    checks: list[CheckResult] = []

    # Environment
    env = getattr(settings, "ENV_NAME", "dev")
    checks.append(CheckResult(name="Environment", status="ok", message=env))

    # Python/Django
    checks.append(
        CheckResult(
            name="Python version",
            status="ok",
            message=".".join(map(str, sys.version_info[:3])),
        )
    )
    import django

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

    try:
        connections["default"].cursor()
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

    # System basics (simple versions of CLI checks)
    disk = run("df -h / | awk 'NR==2 {print $5 \" used (\" $4 \" free)\"}'")
    if disk.returncode == 0:
        checks.append(CheckResult(name="Disk on /", status="ok", message=disk.stdout.strip()))

    load = run("cut -d' ' -f1-3 /proc/loadavg")
    if load.returncode == 0:
        checks.append(CheckResult(name="Load average", status="ok", message=load.stdout.strip()))

    mem = run("free -h | awk 'NR==2 {print $3 \" used / \" $2 \" total\"}'")
    if mem.returncode == 0:
        checks.append(CheckResult(name="Memory", status="ok", message=mem.stdout.strip()))

    return checks


@login_required
@user_passes_test(is_staff)
def status_view(request: HttpRequest) -> HttpResponse:

    if not ip_allowed(request):
        return HttpResponseForbidden("IP not allowed")


    env = getattr(settings, "ENV_NAME", "dev").lower()
    checks = collect_checks()

    # Handle JSON API
    if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
        data = {
            "env": env,
            "checks": [asdict(c) for c in checks],
        }
        return JsonResponse(data)

    # Handle restart (DEV only, POST)
    restart_allowed = env == "dev"
    restart_status: str | None = None

    if request.method == "POST" and restart_allowed:
        bounce_script = "/home/pi/bin/bounce.sh"
        if os.path.exists(bounce_script) and os.access(bounce_script, os.X_OK):
            result = run(bounce_script)
            if result.returncode == 0:
                restart_status = "OK"
            else:
                restart_status = f"FAILED: {result.stderr.strip()}"
        else:
            restart_status = "Bounce script not found or not executable"

    context = {
        "env": env,
        "checks": checks,
        "restart_allowed": restart_allowed,
        "restart_status": restart_status,
    }
    return render(request, "status/dashboard.html", context)
