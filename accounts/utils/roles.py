#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
roles.py
roles
/srv/django/MikesLists_dev/accounts/utils/roles.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 23:59:40"
###############################################################################


def get_user_role(user):
    if user.groups.filter(name="Admins").exists():
        return "admin"
    if user.groups.filter(name="Editors").exists():
        return "editor"
    if user.groups.filter(name="Read Only").exists():
        return "readonly"
    return "unknown"
