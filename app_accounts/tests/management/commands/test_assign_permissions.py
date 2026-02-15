#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_assign_permissions.py
app_accounts.tests.management.commands.test_assign_permissions
/srv/django/MikesLists_dev/app_accounts/tests/management/commands/test_assign_permissions.py




"""
__version__ = "0.0.0.000022-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-14 22:16:44"
###############################################################################

from django.test import TestCase
from django.contrib.auth.models import Group
from app_accounts.management.commands import assign_permissions as assign_perms_command


class AssignPermissionsTestCase(TestCase):
    def setUp(self):
        self.admins_group, _ = Group.objects.get_or_create(name="Admins")
        self.users_group = Group.objects.create(name="Users")

    def test_assign_permissions(self):
        # Run the management command
        assign_perms_command.Command().handle()

        # Admins should have the new permissions
        self.assertTrue(
            self.admins_group.permissions.filter(
                codename="view_own_profile"
            ).exists()
        )

        self.assertTrue(
            self.admins_group.permissions.filter(
                codename="view_own_profile",
                name="Can view own profile"
            ).exists()
        )

        # Users group should NOT have the permission
        self.assertFalse(
            self.users_group.permissions.filter(
                codename="view_own_profile"
            ).exists()
        )
