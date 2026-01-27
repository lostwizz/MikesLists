#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
sync_permissions.py
app_accounts.management.commands.sync_permissions
/srv/django/MikesLists_dev/app_accounts/management/commands/sync_permissions.py



"""
__version__ = "0.0.0.000023-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 12:16:03"
###############################################################################

from django.core.management.base import BaseCommand
from app_accounts.utils.roles import sync_group_permissions

class Command(BaseCommand):
    help = "Syncs cross-app permissions for defined roles."

    def handle(self, *args, **options):
        # Professional structure for role definitions
        ROLE_CONFIG = {
            "Admin_Manager": {
                "app_accounts": ["view_profile", "change_profile"],
                "app_blog": ["add_post", "change_post", "delete_post"],
                "app_reports": ["view_analytics"],
            },
            "Staff_Editor": {
                "app_accounts": ["view_profile"],
                "app_blog": ["add_post", "change_post"],
            }
        }

        for role, apps_data in ROLE_CONFIG.items():
            self.stdout.write(f"Processing Role: {role}...")
            sync_group_permissions(role, apps_data)

        self.stdout.write(self.style.SUCCESS("✅ All groups synced across all apps."))
