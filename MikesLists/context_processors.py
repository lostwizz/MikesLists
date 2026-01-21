#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
context_processors.py
MikesLists.context_processors
/srv/django/MikesLists_dev/MikesLists/context_processors.py

"""
__version__ = "0.0.0.000004-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 17:29:42"
###############################################################################



# MikesLists/context_processors.py
from django.conf import settings


def export_env_vars(request):

    X = getattr(settings, "ENV_NAME", "dev")
    # print(f"@@@{ X=}@@@")
    return {"env": X}


def user_info(request):
    # Username
    username = request.user.username if request.user.is_authenticated else "Guest"

    # Remote IP (handles proxies later if you add nginx)
    ip = request.META.get("HTTP_X_FORWARDED_FOR")
    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")

    return {
        "sidebar_username": username,
        "sidebar_ip": ip,
    }

