#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
context_processors.py
app_core.context_processors
/srv/django/MikesLists_dev/app_core/context_processors.py


"""
__version__ = "0.0.0.000007-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-07 18:25:56"
###############################################################################

# MikesLists/context_processors.py
from django.conf import settings

from app_core.utils.env import is_dev, get_env

def export_env_vars(request):
    # X = getattr(settings, "ENV_NAME", "dev")
    # # print(f"@@@{ X=}@@@")
    return {"env": get_env()}


def user_info(request):
    if request.user.is_authenticated:
        # Username
        username = request.user.username if request.user.is_authenticated else "Guest"

        # Remote IP (handles proxies later if you add nginx)
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")

        # env = getattr(settings, "ENV_NAME", "dev")
        return {
            "sidebar_username": username,
            "sidebar_ip": ip,
            "sidebar_env": get_env(),
            'user_profile': getattr(request.user, 'profile', None),
        }
    return {}
