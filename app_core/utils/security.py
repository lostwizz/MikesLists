#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
security.py
app_core.utils.security
/srv/django/MikesLists_dev/app_core/utils/security.py




"""
__version__ = "0.1.0.000042-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 22:25:43"
###############################################################################


from django.conf import settings
from app_core.utils.ip import get_client_ip, is_ip_allowed_for_admin

def is_admin_access_allowed(request) -> bool:
    """
    Return True if this request is allowed to access admin-only status.
    """
    ip = get_client_ip(request)
    allowed = getattr(settings, "STATUS_ALLOWED_IP_PREFIXES", [])
    return is_ip_allowed_for_admin(ip, allowed)
