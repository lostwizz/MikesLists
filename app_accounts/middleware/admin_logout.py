#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
admin_logout.py
app_accounts.middleware.admin_logout
/srv/django/MikesLists_dev/app_accounts/middleware/admin_logout.py




"""
__version__ = "0.0.0.000013-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-29 00:14:23"
###############################################################################


from django.contrib.auth import logout

class ForceAdminLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # If user logged out of site, also clear admin session
        if request.path == "/accounts/logout/":
            logout(request)

        return response
