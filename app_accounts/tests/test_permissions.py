"""
app_accounts.tests.test_permissions
/srv/django/MikesLists_dev/app_accounts/tests/test_permissions.py

Tests for permission checking and group assignment functionality.
"""

import pytest
from unittest.mock import patch
from django.contrib.auth.models import User, Group, Permission
from app_accounts.permissions import (
    has_permissions,
    get_user_permissions_list,
    ensure_groups_and_permissions,
    assign_permissions,
)


###############################################################################
# has_permissions() Tests
###############################################################################

@pytest.mark.django_db
def test_has_permissions_any_perm_true():
    """
    Test that has_permissions returns True when any_perm=True and at least
    one permission in the list is granted to the user.
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


@pytest.mark.django_db
def test_has_permissions_all_perms_false():
    """
    Test that has_permissions returns False when any_perm=False and not all
    permissions in the list are granted.
    """
    user = User.objects.create_user(username="mike2", password="x")

    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    full_perm = f"{perm.content_type.app_label}.{perm.codename}"

    perm_list = [
        full_perm,            # True
        "nonexistent_perm",   # False → all() should fail
    ]

    assert has_permissions(user, perm_list, any_perm=False) is False


@pytest.mark.django_db
def test_has_permissions_superuser():
    """
    Test that superusers always return True for has_permissions regardless
    of which permissions are checked.
    """
    user = User.objects.create_user(
        username="admin",
        password="x",
        is_superuser=True
    )

    assert has_permissions(user, ["anything"], any_perm=True) is True
    assert has_permissions(user, ["anything"], any_perm=False) is True


###############################################################################
# ensure_groups_and_permissions() Tests
###############################################################################
@pytest.mark.django_db
def test_ensure_groups_and_permissions_missing_permission():
    """
    Ensure a warning is printed when a referenced permission does not exist.
    """
    # Delete a permission the function actually looks for
    Permission.objects.filter(codename="view_own_profile").delete()

    with patch("builtins.print") as mock_print:
        ensure_groups_and_permissions()

    assert any(
        "[WARNING] Permission" in str(call.args[0])
        for call in mock_print.call_args_list
    )



###############################################################################
# assign_permissions() Tests
###############################################################################

@pytest.mark.django_db
def test_assign_permissions_warning_for_missing_permission(capsys):
    """
    Test that assign_permissions() prints a warning when trying to assign
    a permission that doesn't exist in the database. This covers line 140.
    """
    # Delete all the permissions that assign_permissions tries to use
    # This forces the code into the else branch on line 140
    Permission.objects.filter(
        codename__in=[
            "add_node", "change_node", "delete_node", "view_node",
            "view_my_profile", "edit_my_profile"
        ]
    ).delete()

    # Call the actual function
    assign_permissions()

    # Capture the printed output
    captured = capsys.readouterr()

    # Verify the warning was printed
    assert "[WARNING] Permission" in captured.out
    assert "not found" in captured.out



@pytest.mark.django_db
def test_assign_permissions_creates_groups_successfully():
    """
    Test that assign_permissions successfully creates groups and assigns
    permissions when all permissions exist.
    """
    # Ensure at least one permission exists that's used in assign_permissions
    from django.contrib.contenttypes.models import ContentType

    # Get or create a content type for testing
    content_type = ContentType.objects.first()

    # Create the permissions that assign_permissions expects
    Permission.objects.get_or_create(
        codename="view_node",
        defaults={"name": "Can view node", "content_type": content_type}
    )

    # Run the function
    assign_permissions()

    # Verify groups were created
    assert Group.objects.filter(name="Admins").exists()
    assert Group.objects.filter(name="Editors").exists()
    assert Group.objects.filter(name="Read Only").exists()




@pytest.mark.django_db
def test_ensure_groups_and_permissions_executes_assignment():
    """
    Ensures the permission assignment loop runs, covering lines 99–100.
    """
    # Make sure at least one permission exists in the DB
    assert Permission.objects.exists()

    # Call the function — this will execute the missing lines
    ensure_groups_and_permissions()

    # Verify that at least one group has at least one permission assigned
    admins = Group.objects.get(name="Admins")
    assert admins.permissions.exists()
