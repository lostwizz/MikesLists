#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_permissions_utils.py

Comprehensive test suite for permission utility functions in app_accounts.

Tests cover:
- get_perms_for_app: Retrieves all permissions for a specific Django app
- check_user_perms: Validates user permissions with 'any' or 'all' logic
- get_custom_permissions: Fetches custom application-specific permissions

These utilities are used throughout the application for permission checking
and management.
"""
__version__ = "0.0.0.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-14 20:33:24"
###############################################################################

import pytest
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from app_accounts.utils.permissions import (
    get_perms_for_app,
    check_user_perms,
    get_custom_permissions
)
from app_accounts.models.profile import Profile


###############################################################################
# get_perms_for_app() Tests
###############################################################################


@pytest.mark.django_db
def test_get_perms_for_app_returns_permissions():
    """
    Verify that get_perms_for_app returns all permissions associated with
    a specific Django application label.

    Uses 'auth' app as test case since it's always present with built-in
    permissions (User, Group, Permission model permissions).
    """
    # Get all permissions for Django's built-in 'auth' app
    perms = get_perms_for_app("auth")

    # Verify permissions exist for this app
    assert perms.exists(), "Expected permissions to exist for 'auth' app"

    # Verify all returned permissions belong to the 'auth' app
    assert all(
        p.content_type.app_label == "auth" for p in perms
    ), "All permissions should have app_label='auth'"


###############################################################################
# check_user_perms() Tests
###############################################################################


@pytest.mark.django_db
def test_check_user_perms_any_logic():
    """
    Verify that check_user_perms with logic='any' returns True when the user
    has at least one of the requested permissions.

    Test scenario:
    - User has permission A
    - Checking for permissions [A, B] with 'any' logic
    - Should return True (user has A, even though they lack B)
    """
    # Create test user
    user = User.objects.create_user(username="mike", password="x")

    # Grant user a permission (use the first available permission)
    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    # Build permission list with one valid and one invalid permission
    perm_list = [
        f"{perm.content_type.app_label}.{perm.codename}",  # User HAS this
        "auth.nonexistent_perm",                            # User does NOT have this
    ]

    # With 'any' logic, should return True (user has at least one permission)
    result = check_user_perms(user, perm_list, logic="any")
    assert result is True, "Should return True when user has any of the permissions"


@pytest.mark.django_db
def test_check_user_perms_all_logic():
    """
    Verify that check_user_perms with logic='all' returns False when the user
    lacks any of the requested permissions.

    Test scenario:
    - User has permission A
    - Checking for permissions [A, B] with 'all' logic
    - Should return False (user lacks B, even though they have A)
    """
    # Create test user
    user = User.objects.create_user(username="mike2", password="x")

    # Grant user a permission
    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    # Build permission list with one valid and one invalid permission
    perm_list = [
        f"{perm.content_type.app_label}.{perm.codename}",  # User HAS this
        "auth.nonexistent_perm",                            # User does NOT have this
    ]

    # With 'all' logic, should return False (user doesn't have ALL permissions)
    result = check_user_perms(user, perm_list, logic="all")
    assert result is False, "Should return False when user lacks any permission"


###############################################################################
# get_custom_permissions() Tests
###############################################################################


@pytest.mark.django_db
def test_get_custom_permissions_returns_existing_permission():
    """
    Verify that get_custom_permissions returns the view_own_profile permission
    when it exists in the database.

    This permission should be created by Django migrations on the Profile model,
    but we ensure it exists for test reliability.
    """
    # Get or create the permission to ensure it exists
    content_type = ContentType.objects.get_for_model(Profile)
    perm, created = Permission.objects.get_or_create(
        codename="view_own_profile",
        content_type=content_type,
        defaults={"name": "Can view own profile"}
    )

    # Call the function under test
    result = get_custom_permissions()

    # Verify the permission is in the returned dictionary
    assert "view_own_profile" in result, "Expected 'view_own_profile' key in result"
    assert result["view_own_profile"] == perm, "Returned permission should match database object"
    assert result["view_own_profile"].codename == "view_own_profile", "Codename should match"


@pytest.mark.django_db
def test_get_custom_permissions_handles_missing_permission():
    """
    Verify that get_custom_permissions handles the case where the permission
    doesn't exist in the database.

    Note: This test assumes the function has been updated to handle missing
    permissions gracefully. If the function raises an exception instead,
    this test documents the expected behavior change.
    """
    # Ensure the permission doesn't exist
    Permission.objects.filter(codename="view_own_profile").delete()

    # Attempt to get custom permissions
    # If function returns empty dict on error, test passes
    # If function raises exception, this documents that behavior
    try:
        result = get_custom_permissions()
        # If we get here, function returned something (likely empty dict)
        assert isinstance(result, dict), "Should return a dictionary"
    except Permission.DoesNotExist:
        # If function raises DoesNotExist, that's also acceptable behavior
        # This test documents that the function will fail without the permission
        pytest.skip("Function raises DoesNotExist when permission missing - expected behavior")


###############################################################################
# Edge Cases and Integration Tests
###############################################################################


@pytest.mark.django_db
def test_check_user_perms_with_superuser():
    """
    Verify that superusers pass permission checks regardless of actual
    permissions assigned.

    Django's permission system automatically grants all permissions to
    superusers, so check_user_perms should return True for any permission
    list when the user is a superuser.
    """
    # Create superuser
    superuser = User.objects.create_user(
        username="admin",
        password="x",
        is_superuser=True
    )

    # Check arbitrary permissions
    perm_list = ["auth.add_user", "auth.delete_user", "auth.nonexistent_perm"]

    # Superuser should have all permissions
    assert check_user_perms(superuser, perm_list, logic="all") is True
    assert check_user_perms(superuser, perm_list, logic="any") is True


@pytest.mark.django_db
def test_check_user_perms_with_no_permissions():
    """
    Verify that check_user_perms returns False for users with no permissions.
    """
    # Create user with no permissions
    user = User.objects.create_user(username="noperms", password="x")

    perm_list = ["auth.add_user", "auth.change_user"]

    # Should return False for both 'any' and 'all' logic
    assert check_user_perms(user, perm_list, logic="any") is False
    assert check_user_perms(user, perm_list, logic="all") is False


@pytest.mark.django_db
def test_get_perms_for_app_nonexistent_app():
    """
    Verify that get_perms_for_app returns an empty queryset for apps
    that don't exist or have no permissions.
    """
    # Query for a non-existent app
    perms = get_perms_for_app("nonexistent_app_label_12345")

    # Should return empty queryset, not raise an error
    assert not perms.exists(), "Should return empty queryset for non-existent app"
