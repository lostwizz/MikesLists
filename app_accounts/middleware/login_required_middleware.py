#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
login_required_middleware.py
login_required_middleware
/srv/django/MikesLists_dev/app_accounts/middleware/login_required_middleware.py



"""
__version__ = "0.0.0.000013-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 13:30:06"
###############################################################################
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from .models import Profile


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
    # Note: reverse() calls here might fail if URLs aren't loaded yet.
    # Hardcoded strings or moving these inside process_view is safer.
    "/health/",
    "/health"
)

class LoginRequiredMiddleware:


    # ---------------------------------------------------------------------
    def __init__(self, get_response):
        self.get_response = get_response

    # ---------------------------------------------------------------------
    def __call__(self, request):
        # 1. Immediate pass-through for the health check
        if request.path.startswith(('/health/', '/health')):
            return self.get_response(request)

        # 2. Check for authenticated users
        if request.user.is_authenticated:
            return self.get_response(request)

        # 3. Continue the middleware chain
        return self.get_response(request)

    # ---------------------------------------------------------------------
    def process_view(self, request, view_func, view_args, view_kwargs):
        # 1. Skip based on path prefixes
        if request.path.startswith(EXEMPT_PATH_PREFIXES):
            return None

        # 2. Get the view name from the resolver
        view_name = request.resolver_match.view_name if request.resolver_match else ""

        # 3. Skip exempted named URLs
        if view_name in EXEMPT_NAMES:
            return None

        # 4. Enforce login
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))

        return None


class UpdateLastActivityMiddleware:
    """Updates the 'last_seen' timestamp on every request."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update profile timestamp without triggering signals
            Profile.objects.filter(user=request.user).update(last_seen=timezone.now())

        return self.get_response(request)


class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # We use .update() because it's faster and doesn't trigger signals
            Profile.objects.filter(user=request.user).update(last_seen=timezone.now())

        response = self.get_response(request)
        return response
