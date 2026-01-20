#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
assign_permissions.py
accounts.management.commands.assign_permissions
/srv/django/MikesLists_dev/accounts/management/commands/assign_permissions.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 23:09:33"
###############################################################################

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from accounts.permissions import assign_permissions

class Command(BaseCommand):
    help = "Assign permissions to groups"

    def handle(self, *args, **options):
        assign_permissions()
        self.stdout.write(self.style.SUCCESS("Permissions assigned."))



