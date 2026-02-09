#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
view_status.py
app_core.views.status
/srv/django/MikesLists_dev/app_core/views/status.py



"""
__version__ = "0.1.0.000044-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 22:41:13"
###############################################################################


from django.contrib.auth.decorators import user_passes_test
from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
    HttpResponseForbidden,
)
from django.shortcuts import render

from app_core.utils.auth import is_staff
from app_core.utils.env import get_env
from app_core.utils.security import is_admin_access_allowed
from app_core.services.status_service import collect_checks
from app_core.services.restart_service import restart_allowed, perform_restart
from app_accounts.utils.roles import get_user_role


# ---------------------------------------------------------------------------
@user_passes_test(is_staff)
def status_view(request: HttpRequest) -> HttpResponse:
    """
    Main system status dashboard.
    Staff-only, and IP-restricted via is_admin_access_allowed().
    """

    if not is_admin_access_allowed(request):
        return HttpResponseForbidden("IP not allowed")

    checks = collect_checks()

    # JSON API mode
    if (
        request.headers.get("Accept") == "application/json"
        or request.GET.get("format") == "json"
    ):
        return JsonResponse(
            {
                "env": get_env(),
                "checks": [c.__dict__ for c in checks],
            }
        )

    # Restart logic (delegated to restart_service)
    restart_status = None
    if request.method == "POST" and restart_allowed():
        success, msg = perform_restart()
        restart_status = msg

    context = {
        "env": get_env(),
        "checks": checks,
        "restart_allowed": restart_allowed(),
        "restart_status": restart_status,
    }

    return render(request, "app_core/status/dashboard.html", context)


# ---------------------------------------------------------------------------
def dashboard(request):
    """
    Role-based dashboard routing.
    """
    role = get_user_role(request.user)

    template = {
        "admin": "app_core/dashboard/admin.html",
        "editor": "app_core/dashboard/editor.html",
    }.get(role, "app_core/dashboard/readonly.html")

    return render(request, template)
