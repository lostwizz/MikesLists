#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
decorators.py
app_core.utils.decorators
/srv/django/MikesLists_dev/app_core/utils/decorators.py


Environment-based view access decorators.


# Optional: Custom permission/group decorators


__version__ = "0.0.0.000032-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-11 23:24:21"
"""
###############################################################################
from __future__ import annotations
from functools import wraps
from django.http import HttpResponseForbidden
from app_core.utils.env import AppEnv, get_env_enum



# -----------------------------------------------------------------
def require_env(*allowed_envs: AppEnv):
    """
    Generic decorator factory:
        @require_env(AppEnv.DEV)
        @require_env(AppEnv.TEST, AppEnv.LIVE)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            current = get_env_enum()
            if current not in allowed_envs:
                allowed = ", ".join(env.value for env in allowed_envs)
                return HttpResponseForbidden(
                    f"This view is only available in: {allowed}"
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# -----------------------------------------------------------------
# Convenience decorators
# def dev_only(view_func):
def require_dev_env(view_func):
    return require_env(AppEnv.DEV)(view_func)


# -----------------------------------------------------------------
def require_test_env(view_func):
    return require_env(AppEnv.TEST)(view_func)


# -----------------------------------------------------------------
# def live_only(view_func):
def require_live_env(view_func):
    return require_env(AppEnv.LIVE)(view_func)


# -----------------------------------------------------------------
def require_non_dev_only(view_func):
    """Allow only TEST or LIVE."""
    return require_env(AppEnv.TEST, AppEnv.LIVE)(view_func)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
