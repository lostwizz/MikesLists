#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_assign_permissions.py
app_accounts.tests.management.commands.test_assign_permissions
/srv/django/MikesLists_dev/app_accounts/tests/management/commands/test_assign_permissions.py




"""
__version__ = "0.0.0.000020-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-26 23:09:49"
###############################################################################


from django.test import TestCase
# from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import Group
# from app_accounts.permissions import assign_permissions
# from app_accounts.management.commands import assign_permissions
from app_accounts.management.commands import assign_permissions as assign_perms_command
from app_accounts.models import Profile
from app_accounts.permissions import assign_permissions

class AssignPermissionsTestCase(TestCase):
    def setUp(self):
        self.admins_group, _ = Group.objects.get_or_create(name="Admins")
        self.users_group = Group.objects.create(name="Users")

    def test_assign_permissions(self):
        assign_perms_command.Command().handle()

        self.assertTrue(
            self.admins_group.permissions.filter(
                codename="view_my_profile", name="Can view my profile"
            ).exists()
        )

        self.assertFalse(
            self.users_group.permissions.filter(
                codename="view_my_profile", name="Can view my profile"
            ).exists()
        )



    # def test_user_count():
    #     from django.contrib.auth.models import User
    #     assert User.objects.count() == 0
