#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_services.py

Tests for user registration and management services.
"""
###############################################################################

import pytest
from unittest.mock import patch
from django.contrib.auth.models import User

# from app_accounts.services.services import UserRegistrationService, UserLifecycleService
# from app_accounts.services import UserRegistrationService, UserLifecycleService

from app_accounts.services.user_lifecycle_service import UserLifecycleService
from app_accounts.services.user_registration_service import UserRegistrationService

from app_accounts.models.profile import Profile


###############################################################################
# UserRegistrationService Tests
###############################################################################


@pytest.mark.django_db
@patch("app_accounts.services.user_registration_service.assign_role_to_user")
def test_register_new_user(mock_assign_role):
    data = {
        "username": "mike",
        "email": "mike@example.com",
        "password": "secret",
        "bio": "Hello world",
    }

    user = UserRegistrationService.register_new_user(data)

    assert user.username == "mike"
    assert user.email == "mike@example.com"

    assert hasattr(user, "profile")
    user.profile.refresh_from_db()
    assert user.profile.bio == "Hello world"

    mock_assign_role.assert_called_once_with(user, "Viewer")


@pytest.mark.django_db
def test_lifecycle_register_user():
    """
    Test the complete user registration lifecycle without mocking.
    This covers lines 54-57 in UserLifecycleService.register_user()
    """
    user = UserLifecycleService.register_user(
        username="john", email="john@example.com", password="secret123", role="Viewer"
    )

    assert User.objects.filter(username="john").exists()
    assert user.check_password("secret123")

    # Verify profile (should be auto-created by signal)
    profile = Profile.objects.get(user=user)
    assert profile is not None


@pytest.mark.django_db
def test_lifecycle_register_user_custom_role():
    """
    Test user registration with a custom role.
    This also covers lines 54-57 with a different role parameter.
    """
    user = UserLifecycleService.register_user(
        username="admin_user",
        email="admin@example.com",
        password="adminpass",
        role="Admins",
    )

    assert User.objects.filter(username="admin_user").exists()
    assert user.email == "admin@example.com"


###############################################################################
# UserLifecycleService.delete_user_safely() Tests
###############################################################################


@pytest.mark.django_db
def test_delete_user_safely():
    """
    Test that users and their associated profiles can be safely deleted.
    This covers lines 63-66 in UserLifecycleService.delete_user_safely()
    """
    user = User.objects.create_user(username="temp", password="x")
    # Profile auto-created by signal

    user_id = user.id

    # Delete the user using the service
    result = UserLifecycleService.delete_user_safely(user_id)

    # Verify the method returned True
    assert result is True

    # Verify user is gone
    assert not User.objects.filter(id=user_id).exists()
    # Profile should be cascade deleted
    assert not Profile.objects.filter(user_id=user_id).exists()


@pytest.mark.django_db
def test_delete_user_safely_with_multiple_users():
    """
    Test that deleting one user doesn't affect others.
    Additional coverage for delete_user_safely()
    """
    user1 = User.objects.create_user(username="user1", password="x")
    user2 = User.objects.create_user(username="user2", password="x")

    user1_id = user1.id

    # Delete only user1
    UserLifecycleService.delete_user_safely(user1_id)

    # user1 should be gone
    assert not User.objects.filter(id=user1_id).exists()
    # user2 should still exist
    assert User.objects.filter(id=user2.id).exists()


###############################################################################
# UserLifecycleService.promote_user() Tests
###############################################################################

# @pytest.mark.django_db
# @patch("app_accounts.utils.assign_role_to_user")
# def test_promote_user(mock_assign_role):
#     """
#     Test promoting a user to a new role.
#     This covers line 72 in UserLifecycleService.promote_user()
#     """
#     user = User.objects.create_user(username="bob", password="x")
#     # Profile auto-created by signal

#     # Mock the assign_role_to_user to return True
#     mock_assign_role.return_value = True

#     # Promote the user
#     result = UserLifecycleService.promote_user(user, "Admins")

#     # Verify assign_role_to_user was called with clear_existing=True
#     mock_assign_role.assert_called_once_with(user, "Admins", clear_existing=True)

#     # Verify the result
#     assert result is True


# @pytest.mark.django_db
# @patch("app_accounts.utils.assign_role_to_user")
# def test_promote_user_clears_existing_roles(mock_assign_role):
#     """
#     Test that promote_user clears existing roles when promoting.
#     Additional coverage for line 72.
#     """
#     user = User.objects.create_user(username="alice", password="x")

#     mock_assign_role.return_value = True

#     # Promote to Editors
#     UserLifecycleService.promote_user(user, "Editors")

#     # Verify clear_existing=True was passed
#     assert mock_assign_role.call_args[1]['clear_existing'] is True


@pytest.mark.django_db
@patch("app_accounts.services.user_lifecycle_service.assign_role_to_user")
def test_promote_user(mock_assign_role):
    user = User.objects.create_user(username="bob", password="x")
    mock_assign_role.return_value = True

    result = UserLifecycleService.promote_user(user, "Admins")
    assert result

    mock_assign_role.assert_called_once_with(user, "Admins", clear_existing=True)


@pytest.mark.django_db
@patch("app_accounts.services.user_lifecycle_service.assign_role_to_user")
def test_promote_user_clears_existing_roles(mock_assign_role):
    user = User.objects.create_user(username="alice", password="x")
    mock_assign_role.return_value = True

    UserLifecycleService.promote_user(user, "Editors")

    assert mock_assign_role.call_args[1]["clear_existing"] is True
