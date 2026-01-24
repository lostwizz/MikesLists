#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
assign_permissions.py
app_accounts.management.commands.assign_permissions
/srv/django/MikesLists_dev/app_accounts/management/commands/assign_permissions.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:00:28"
###############################################################################

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from app_accounts.permissions import assign_permissions

class Command(BaseCommand):
    help = "Assign permissions to groups"

    def handle(self, *args, **options):
        assign_permissions()
        self.stdout.write(self.style.SUCCESS("Permissions assigned."))
