#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_assign_permissions.py
test_assign_permissions.py
/srv/django/MikesLists_dev/accounts/tests/management/commands/test_assign_permissions.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 21:59:42"
###############################################################################


from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from accounts.management.commands import assign_permissions


class AssignPermissionsTestCase(TestCase):
    def setUp(self):
        self.admins_group = Group.objects.create(name="Admins")
        self.users_group = Group.objects.create(name="Users")

    def test_assign_permissions(self):
        assign_permissions.Command().handle()

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
