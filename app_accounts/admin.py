#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
admin.py
app_accounts.admin
/srv/django/MikesLists_dev/app_accounts/admin.py



"""
__version__ = "0.0.0.000070-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:06:44"
###############################################################################

from django.contrib import admin
from .models.profile import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Add 'last_seen' so you can monitor activity in the Admin UI
    list_display = ('user', 'email', 'theme_preference', 'email_notifications', 'last_seen')
    list_filter = ('theme_preference', 'email_notifications')
    search_fields = ('user__username', 'user__email')
