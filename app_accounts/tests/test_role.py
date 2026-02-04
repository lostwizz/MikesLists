#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_role.py
app_accounts.tests.test_role
/srv/django/MikesLists_dev/app_accounts/tests/test_role.py




"""
__version__ = "0.0.0.000026-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-02 14:16:25"
###############################################################################


# app_accounts/tests/test_role.py
import pytest
from app_accounts.models.role import Role

@pytest.mark.django_db
def test_role_manager_create_role():
    role = Role.objects.create_role(name="TestRole")
    assert role.name == "TestRole"
    assert Role.objects.filter(name="TestRole").exists()
