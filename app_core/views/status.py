#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
view_status.py
app_core.views.status
/srv/django/MikesLists_dev/app_core/views/status.py



"""
__version__ = "0.1.0.000048-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-09 21:54:16"
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
# from app_core.utils.ip import get_client_ip
from app_core.utils import net, ip
from app_core.utils.security import is_admin_access_allowed
from app_core.services.restart_service import restart_allowed, perform_restart
from app_accounts.utils.roles import get_user_role

from app_core.services import status_service



# ---------------------------------------------------------------------------
def status(request):
    return JsonResponse(status_service.get_status())


# ---------------------------------------------------------------------------
@user_passes_test(is_staff)
def status_view(request: HttpRequest) -> HttpResponse:

    if not is_admin_access_allowed(request):
        return HttpResponseForbidden("IP not allowed")

    status_data = status_service.get_status(request)

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

    # Restart logic
    restart_status = None
    if request.method == "POST" and restart_allowed():
        success, msg = perform_restart()
        restart_status = msg

    return render(request, "app_core/status/dashboard.html", status_data)


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
