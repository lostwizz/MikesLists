#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
permissions.py
app_accounts.permissions
/srv/django/MikesLists_dev/app_accounts/permissions.py





- Use permissions in your code
    In views:
        @permission_required("todo.view_items")
        def view_items(request):
            ...

    In templates:
        {% if perms.todo.view_items %}
            <a href="/items/">View Items</a>
        {% endif %}
OR:

Use permissions in your view
        from django.contrib.auth.decorators import permission_required

        @permission_required("todo.view_items")
        def item_list(request):
            ...

            from django.contrib.auth.mixins import PermissionRequiredMixin
            class ItemListView(PermissionRequiredMixin, ListView):
                permission_required = "todo.view_items"

Use permissions in template
        {% if perms.todo.view_items %}
            <a href="/items/">View Items</a>
        {% endif %}


Use groups in your signals (you already do this
        group = Group.objects.get(name="Read Only")
        instance.groups.add(group)




"""
__version__ = "0.0.0.000027-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-14 22:14:55"
###############################################################################

from django.contrib.auth.models import Group, Permission


# ---------------------------------------------------------------------------
# CANONICAL SINGLE SOURCE OF TRUTH
# ---------------------------------------------------------------------------
GROUP_PERMISSIONS = {
    "Admins": [
        "add_node", "change_node", "delete_node", "view_node",
        "view_own_profile", "edit_own_profile",
    ],
    "Editors": [
        "change_node", "view_node",
    ],
    "Read Only": [
        "view_node", "view_own_profile",
    ],
}


# ---------------------------------------------------------------------------
# CANONICAL ASSIGNMENT FUNCTION
# ---------------------------------------------------------------------------
def assign_permissions():
    """
    Canonical permission assignment function.
    Used by management command and tests.
    """
    for group_name, perm_codenames in GROUP_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)

        for codename in perm_codenames:
            perm = Permission.objects.filter(codename=codename).first()
            if perm:
                group.permissions.add(perm)
            else:
                print(f"[WARNING] Permission '{codename}' not found")


# ---------------------------------------------------------------------------
# LEGACY WRAPPER (kept for compatibility)
# ---------------------------------------------------------------------------
def ensure_groups_and_permissions():
    """
    Legacy-compatible wrapper.
    Calls the canonical assign_permissions() so tests and
    management commands behave identically.
    """
    assign_permissions()


# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS (unchanged)
# ---------------------------------------------------------------------------
def has_permissions(user, perm_list, any_perm=False):
    if user.is_superuser:
        return True

    if any_perm:
        results = []
        for perm in perm_list:
            results.append(user.has_perm(perm))
        return any(results)

    return all(user.has_perm(perm) for perm in perm_list)


def get_user_permissions_list(user):
    """Returns a readable list of all permission codenames for a user."""
    return list(user.get_all_permissions())
