#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_permissions.py
app_accounts.tests.test_permissions
/srv/django/MikesLists_dev/app_accounts/tests/test_permissions.py




"""
__version__ = "0.0.0.000026-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 13:11:37"
###############################################################################



import pytest
from django.urls import reverse
from django.contrib.auth.models import Group, Permission, User
from app_accounts.permissions import assign_permissions
# from app_accounts.permissions import assign_permissions
from app_accounts.management.commands.assign_permissions import Command
from django.core.exceptions import PermissionDenied

@pytest.mark.django_db
def test_groups_are_created():
    assign_permissions()

    assert Group.objects.filter(name="Admins").exists()
    assert Group.objects.filter(name="Editors").exists()
    assert Group.objects.filter(name="Read Only").exists()

@pytest.mark.django_db
def test_admin_permissions_assigned():
    # 1. Manually trigger the sync logic
    from app_accounts.utils.roles import sync_group_permissions

    # 2. Define exactly what we expect for the test
    perms = {
        "app_accounts": ["view_profile", "change_profile"],
        # Add the other apps/perms your test expects here
    }

    # 3. Use the utility to sync
    sync_group_permissions("Admins", perms)

    admins = Group.objects.get(name="Admins")
    # Now the check should pass
    assert admins.permissions.filter(codename="view_profile").exists()


@pytest.mark.django_db
def test_idempotent_assign_permissions():
    assign_permissions()
    first_count = Permission.objects.count()

    assign_permissions()
    second_count = Permission.objects.count()

    assert first_count == second_count

@pytest.fixture
def admin_group(db):
    """Creates the 'Admins' group for tests."""
    group, _ = Group.objects.get_or_create(name='Admins')
    return group

@pytest.fixture
def admin_user(db, admin_group):
    """Creates a user and adds them to the 'Admins' group."""
    user = User.objects.create_user(username='admin_user', password='password123')
    user.groups.add(admin_group)
    return user

@pytest.fixture
def regular_user(db):
    """Creates a standard user with no special groups."""
    return User.objects.create_user(username='regular_user', password='password123')

@pytest.mark.django_db
class TestGroupManagerAccess:

    def test_unauthenticated_user_redirects(self, client):
        """Guests should be redirected to the login page."""
        url = reverse('accounts:group_manager')
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_regular_user_denied(self, client, regular_user):
        """Users NOT in the Admins group should get a 403 Forbidden error."""
        client.login(username='regular_user', password='password123')
        url = reverse('accounts:group_manager')
        response = client.get(url)
        # Note: If you use PermissionDenied, Django returns status 403
        assert response.status_code == 403

    def test_admin_user_allowed(self, client, admin_user):
        """Users in the Admins group should successfully access the page."""
        client.login(username='admin_user', password='password123')
        url = reverse('accounts:group_manager')
        response = client.get(url)
        assert response.status_code == 200
        assert "User" in response.content.decode()  # Check if table content exists
