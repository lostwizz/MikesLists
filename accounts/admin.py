#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
admin.py
accounts.admin
/srv/django/MikesLists_dev/accounts/admin.py


"""
__version__ = "0.0.0.000070-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 23:17:49"
###############################################################################

from django.contrib import admin
from .models.profile import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme_preference', 'email_notifications')
