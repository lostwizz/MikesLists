#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
permissions.py
app_accounts.utils.permissions
/srv/django/MikesLists_dev/app_accounts/utils/permissions.py



# New: logic for checking/syncing permissions

"""
__version__ = "0.0.0.000024-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-14 20:28:39"
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



def get_custom_permissions():
    """Returns custom permissions if they exist."""
    try:
        return {
            "view_own_profile": Permission.objects.get(
                codename="view_own_profile",
                name="Can view own profile",
            )
        }
    except Permission.DoesNotExist:
        return {}
