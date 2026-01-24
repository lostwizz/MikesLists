#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
permissions.py
app_accounts.views.permissions
/srv/django/MikesLists_dev/app_accounts/views/permissions.py




"""
__version__ = "0.0.0.000004-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:05:14"
###############################################################################



from django.contrib.auth.models import Permission

class CustomPermissions:
    view_my_profile = Permission.objects.get(codename='view_my_profile', name='Can view my profile')
