#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
user_helpers.py
user_helpers
/srv/django/MikesLists_dev/app_accounts/utils/user_helpers.py



# New: User-specific shortcuts (status checks, etc.)





"""
__version__ = "0.0.0.000021-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 11:14:35"
###############################################################################

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

def get_active_users():
    return User.objects.filter(is_active=True)

def toggle_user_status(user_id):
    """Utility to quickly enable/disable a user."""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return user.is_active
