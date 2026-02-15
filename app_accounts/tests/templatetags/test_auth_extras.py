"""
test_auth_extras
/srv/django/MikesLists_dev/app_accounts/tests/templatetags/test_auth_extras.py

Tests for custom Django template tags and filters for authentication.
"""
import pytest
from django.contrib.auth.models import User, Group, Permission

from app_accounts.templatetags.auth_extras import has_group, get_user_role
# from app_accounts.templatetags.auth_extras import get_user_role
from app_accounts.permissions import has_permissions, get_user_permissions_list


###############################################################################
# has_group() Template Filter Tests
###############################################################################

@pytest.mark.django_db
def test_has_group_superuser_returns_true():
    """
    Test that superusers return True for has_group regardless of actual
    group membership.
    """
    user = User.objects.create_user(
        username="root",
        password="x",
        is_superuser=True
    )
    assert has_group(user, "Admins") is True
    assert has_group(user, "NonExistentGroup") is True


@pytest.mark.django_db
def test_has_group_user_in_group_returns_true():
    """
    Test that has_group returns True when the user is a member of the
    specified group.
    """
    user = User.objects.create_user(username="alice", password="x")
    group, _ = Group.objects.get_or_create(name="Admins")
    user.groups.add(group)

    assert has_group(user, "Admins") is True


@pytest.mark.django_db
def test_has_group_user_not_in_group_returns_false():
    """
    Test that has_group returns False when the user is not a member of
    the specified group.
    """
    user = User.objects.create_user(username="bob", password="x")
    Group.objects.get_or_create(name="Admins")

    assert has_group(user, "Admins") is False


@pytest.mark.django_db
def test_has_group_nonexistent_group_returns_false():
    """
    Test that has_group returns False when checking for a group that
    doesn't exist in the database.
    """
    user = User.objects.create_user(username="charlie", password="x")

    assert has_group(user, "NonExistentGroup") is False


###############################################################################
# get_user_role() Template Tag Tests
###############################################################################

@pytest.mark.django_db
def test_get_user_role_returns_group_name():
    """
    Test that get_user_role returns the name of the user's first group.
    """
    user = User.objects.create_user(username="member", password="x")
    group, _ = Group.objects.get_or_create(name="Editors")
    user.groups.add(group)

    result = get_user_role(user)

    assert result == "Editors"


@pytest.mark.django_db
def test_get_user_role_returns_guest_for_no_groups():
    """
    Test that get_user_role returns "Guest" when the user is not a member
    of any groups.
    """
    user = User.objects.create_user(username="nogroup", password="x")

    # Remove any auto-assigned groups to test the "Guest" fallback
    user.groups.clear()

    result = get_user_role(user)

    assert result == "Guest"


@pytest.mark.django_db
def test_get_user_role_returns_first_group_when_multiple():
    """
    Test that get_user_role returns the first group when a user belongs
    to multiple groups.
    """
    user = User.objects.create_user(username="multi", password="x")

    # Add multiple groups
    group1, _ = Group.objects.get_or_create(name="Admins")
    group2, _ = Group.objects.get_or_create(name="Editors")

    user.groups.add(group1)
    user.groups.add(group2)

    result = get_user_role(user)

    # Should return the first group (order may vary by database)
    assert result in ["Admins", "Editors"]


###############################################################################
# has_permissions() Tests (from permissions module)
###############################################################################

@pytest.mark.django_db
def test_has_permissions_any_perm_true():
    """
    Test that has_permissions returns True when any_perm=True and at least
    one permission is granted.
    """
    user = User.objects.create_user(username="mike", password="x")

    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    full_perm = f"{perm.content_type.app_label}.{perm.codename}"

    perm_list = [
        full_perm,            # True
        "nonexistent_perm",   # False
    ]

    assert has_permissions(user, perm_list, any_perm=True) is True


###############################################################################
# get_user_permissions_list() Tests
###############################################################################

@pytest.mark.django_db
def test_get_user_permissions_list_returns_list_of_permissions():
    """
    Test that get_user_permissions_list returns a list of permission strings
    in the format 'app_label.codename'.
    """
    user = User.objects.create_user(username="mike3", password="x")

    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    result = get_user_permissions_list(user)

    assert isinstance(result, list)

    expected = f"{perm.content_type.app_label}.{perm.codename}"
    assert expected in result


@pytest.mark.django_db
def test_get_user_permissions_list_empty_for_no_permissions():
    """
    Test that get_user_permissions_list returns an empty list for users
    with no permissions (after clearing any auto-assigned groups and permissions).
    """
    user = User.objects.create_user(username="noperms", password="x")

    # Clear any auto-assigned groups (which may have permissions)
    user.groups.clear()
    # Clear any auto-assigned direct permissions
    user.user_permissions.clear()

    result = get_user_permissions_list(user)

    assert isinstance(result, list)
    assert len(result) == 0
