#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_permissions.py
accounts.tests.test_permissions
/srv/django/MikesLists_dev/accounts/tests/test_permissions.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 23:29:19"
###############################################################################



import pytest
from django.contrib.auth.models import Group, Permission
from accounts.permissions import assign_permissions

@pytest.mark.django_db
def test_groups_are_created():
    assign_permissions()

    assert Group.objects.filter(name="Admins").exists()
    assert Group.objects.filter(name="Editors").exists()
    assert Group.objects.filter(name="Read Only").exists()

@pytest.mark.django_db
def test_admin_permissions_assigned():
    assign_permissions()
    admins = Group.objects.get(name="Admins")

    expected = [
        "add_lists", "change_lists", "delete_lists", "view_lists",
        "add_items", "change_items", "delete_items", "view_items",
        "view_my_profile", "edit_my_profile",
    ]

    for codename in expected:
        assert admins.permissions.filter(codename=codename).exists()

@pytest.mark.django_db
def test_idempotent_assign_permissions():
    assign_permissions()
    first_count = Permission.objects.count()

    assign_permissions()
    second_count = Permission.objects.count()

    assert first_count == second_count
