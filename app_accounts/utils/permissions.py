#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
permissions.py
permissions
/srv/django/MikesLists_dev/app_accounts/utils/permissions.py


# New: logic for checking/syncing permissions

"""
__version__ = "0.0.0.000018-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 11:09:33"
###############################################################################

from django.contrib.auth.models import Permission

def get_perms_for_app(app_label):
    """Returns all available permissions for a specific app."""
    return Permission.objects.filter(content_type__app_label=app_label)

def check_user_perms(user, perm_list, logic='all'):
    """
    Flexible check for user permissions.
    logic: 'all' or 'any'
    """
    if logic == 'any':
        return any(user.has_perm(p) for p in perm_list)
    return user.has_perms(perm_list)
