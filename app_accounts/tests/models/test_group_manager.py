#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from django.contrib.auth.models import Permission, Group
from app_accounts.models.group_manager import GroupManager


@pytest.mark.django_db
def test_create_role_with_permissions_hits_permission_branch():
    # Arrange: create a permission
    perm = Permission.objects.first()
    assert perm is not None, "At least one permission must exist for this test"

    # Use the custom manager directly
    manager = GroupManager()
    manager.model = Group  # required so the manager knows what model it manages

    # Act
    group = manager.create_role("TestRole", permissions=[perm])

    # Assert
    assert group.permissions.filter(id=perm.id).exists()


@pytest.mark.django_db
def test_get_by_name_returns_group():
    # Arrange
    group = Group.objects.create(name="LookupRole")

    manager = GroupManager()
    manager.model = Group

    # Act
    result = manager.get_by_name("LookupRole")

    # Assert
    assert result == group
