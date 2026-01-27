#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
roles.py
roles
/srv/django/MikesLists_dev/app_accounts/utils/roles.py

# Existing: Group/Role definitions and logic

"""
__version__ = "0.0.0.000014-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 12:16:33"
###############################################################################



from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

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


def get_user_role(user):
    """
    Returns a string representing the user's highest role.
    """
    if not user or user.is_anonymous:
        return "anonymous"
    if user.is_superuser:
        return "admin"
    if user.is_staff:
        return "staff"

    # Optional: If you use Django Groups for roles
    # if user.groups.filter(name="Manager").exists():
    #     return "manager"

    return "user"



def sync_group_permissions(group_name, permissions_dict):
    """
    Syncs a group with permissions from multiple apps.
    :param group_name: Name of the group (e.g., 'Manager')
    :param permissions_dict: { 'app_label': ['codename1', 'codename2'], ... }
    """
    group, _ = Group.objects.get_or_create(name=group_name)

    # Build a complex query: (app=X AND code=Y) OR (app=A AND code=B)
    query = Q()
    for app_label, codenames in permissions_dict.items():
        query |= Q(content_type__app_label=app_label, codename__in=codenames)

    perms = Permission.objects.filter(query)

    # .set() replaces all existing perms with this new list
    group.permissions.set(perms)
    return group
def assign_role_to_user(user, role_name, clear_existing=False):
    """
    Assigns a group-based role to a user.
    """
    try:
        group = Group.objects.get(name=role_name)
        if clear_existing:
            user.groups.clear()
        user.groups.add(group)
        return True
    except Group.DoesNotExist:
        return False
