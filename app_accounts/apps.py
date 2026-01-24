#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
apps.py
app_accounts.apps
/srv/django/MikesLists_dev/app_accounts/apps.py



"""
__version__ = "0.0.0.000070-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 22:06:41"
###############################################################################

from django.apps import AppConfig
from django.db.models.signals import post_migrate

# ---------------------------------------------------------------------
def run_setup_permissions(sender, **kwargs):
    """
    This runs only AFTER migrations are complete,
    preventing the 'RuntimeWarning' and database locks.
    """
    from .permissions import ensure_groups_and_permissions
    try:
        ensure_groups_and_permissions()
    except Exception as e:
        # Fixed the typo in the print statement
        print(f"Error during AppAccountsConfig setup: {e}")

# ---------------------------------------------------------------------
class AppAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_accounts"

    def ready(self):
        # Import signals if you have them
        from .models import signals

        # Connect to post_migrate instead of running immediately
        post_migrate.connect(run_setup_permissions, sender=self)
