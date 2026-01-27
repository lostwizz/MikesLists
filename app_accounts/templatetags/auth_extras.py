#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
auth_extras.py
auth_extras
/srv/django/MikesLists_dev/app_accounts/templatetags/auth_extras.py



"""
__version__ = "0.0.0.000018-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 13:33:42"
###############################################################################

from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() or user.is_superuser


register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """Usage: {% if request.user|has_group:"Admins" %}"""
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()

@register.simple_tag
def get_user_role(user):
    """Returns the name of the user's primary group."""
    group = user.groups.first()
    return group.name if group else "Guest"
