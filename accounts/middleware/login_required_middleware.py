#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
login_required_middleware.py
login_required_middleware
/srv/django/MikesLists_dev/accounts/middleware/login_required_middleware.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 18:46:47"
###############################################################################
from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_NAMES = {
    "accounts:login",
    "accounts:logout",
    "accounts:register",
    "accounts:password_reset",
    "accounts:password_reset_done",
    "accounts:password_reset_confirm",
    "accounts:password_reset_complete",
}

EXEMPT_PATH_PREFIXES = (
    "/static/",
    "/admin/",
    "/favicon.ico",
)


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):

        # Skip static/admin/favicon
        if request.path.startswith(EXEMPT_PATH_PREFIXES):
            return None

        # Now resolver_match is ALWAYS valid
        view_name = request.resolver_match.view_name

        # Skip exempted named URLs
        if view_name in EXEMPT_NAMES:
            return None

        # Enforce login
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))

        return None

