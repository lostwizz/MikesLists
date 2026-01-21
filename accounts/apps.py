#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
apps.py
accounts.apps
/srv/django/MikesLists_dev/accounts/apps.py


"""
__version__ = "0.0.0.000070-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 17:58:13"
###############################################################################

from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from .models import signals
        from .permissions import ensure_groups_and_permissions

        try:
            ensure_groups_and_permissions()
        except Exception as e:
            print(f"Error during AccountsConfig.ready(): {e}")


