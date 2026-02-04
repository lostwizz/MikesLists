#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
role.py
app_accounts.models.role
/srv/django/MikesLists_dev/app_accounts/models/role.py



"""
__version__ = "0.0.0.000025-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-02 13:49:12"
###############################################################################


# app_accounts/models/role.py (or __init__.py)
from django.contrib.auth.models import Group
from .group_manager import GroupManager

class Role(Group):
    objects = GroupManager()

    class Meta:
        proxy = True
