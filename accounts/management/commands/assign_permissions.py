#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
assign_permissions.py
assign_permissions
/srv/django/MikesLists_dev/accounts/management/commands/assign_permissions.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 17:03:09"
###############################################################################

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Assign permissions to groups"

    def handle(self, *args, **options):
        # Assign permissions to groups
        admins_group = Group.objects.get(name="Admins")
        # users_group = Group.objects.get(name="Users")

        admins_group.permissions.add(
            Permission.objects.get(
                codename="view_my_profile", name="Can view my profile"
            )
        )
