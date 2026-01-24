#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
roles.py
roles
/srv/django/MikesLists_dev/app_accounts/utils/roles.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:03:41"
###############################################################################



from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView
from functools import wraps
from django.core.exceptions import PermissionDenied

def require_group(*group_names):
    def decorator(view_func):

        # Do NOT wrap Django's built-in auth views
        if isinstance(view_func, type) and issubclass(view_func, LogoutView):
            return view_func
        if isinstance(view_func, type) and issubclass(view_func, LoginView):
            return view_func
        if isinstance(view_func, type) and issubclass(view_func, PasswordResetView):
            return view_func

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if not request.user.groups.filter(name__in=group_names).exists():
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
