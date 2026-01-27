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
__version__ = "0.0.0.000014-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 11:01:39"
###############################################################################

import logging


from django.contrib.auth.models import Group, Permission


logger = logging.getLogger(__name__)


from django.contrib.auth.models import Group, Permission
from django.apps import apps
from django.db.models import Q
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

GROUPS = {
    "Admins": {
        # "lists": ["add", "change", "delete", "view"],
        # "items": ["add", "change", "delete", "view"],
        "app_accounts": ["view_my_profile", "edit_my_profile"],
    },
    "Editors": {
        # "lists": ["change", "view"],
        # "items": ["change", "view"],
    },
    "Read Only": {
        # "lists": ["view"],
        # "items": ["view"],
        "app_accounts": ["view_my_profile"],
    },
}

def ensure_groups_and_permissions():
    print("[INFO] Starting permission assignment")

    # Clean up any typo groups
    valid_names = set(GROUPS.keys())
    Group.objects.exclude(name__in=valid_names).delete()

    for group_name, app_perms in GROUPS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        print(f"[INFO] Group ensured: {group_name}")

        perms_to_assign = []

        for app_label, codename_roots in app_perms.items():
            for codename_root in codename_roots:
                codename = f"{codename_root}_{app_label}" if "_" not in codename_root else codename_root
                try:
                    perm = Permission.objects.get(codename=codename)
                    perms_to_assign.append(perm)
                    print(f"[INFO] Assigned {codename} to {group_name}")
                except Permission.DoesNotExist:
                    print(f"[WARNING] Permission '{codename}' not found")

        group.permissions.set(perms_to_assign)

    logger.info("Permission assignment complete")





def assign_permissions():
    """
    Logic to ensure groups exist and have the correct permissions.
    """
    # 1. Define Groups
    groups = {
        "Admins": [
            "add_node", "change_node", "delete_node", "view_node",
            "view_my_profile", "edit_my_profile"
        ],
        "Editors": [
            "change_node", "view_node"
        ],
        "Read Only": [
            "view_node", "view_my_profile"
        ],
    }

    for group_name, perms in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)

        for perm_codename in perms:
            # We use codename because it's more reliable
            perm = Permission.objects.filter(codename=perm_codename).first()
            if perm:
                group.permissions.add(perm)
                # Use a simple print or logging if you want to see it in the test output
            else:
                print(f"[WARNING] Permission '{perm_codename}' not found")


def has_permissions(user, perm_list, any_perm=False):
    """
    Checks if a user has a list of permissions.
    :param any_perm: If True, returns True if user has AT LEAST ONE in the list.
    """
    if any_perm:
        return any(user.has_perm(perm) for perm in perm_list)
    return user.has_perms(perm_list)

def get_user_permissions_list(user):
    """Returns a readable list of all permission codenames for a user."""
    return user.get_all_permissions()
