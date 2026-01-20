#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
permissions.py
accounts.permissions
/srv/django/MikesLists_dev/accounts/permissions.py



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
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 23:31:44"
###############################################################################

import logging


from django.contrib.auth.models import Group, Permission


logger = logging.getLogger(__name__)


def assign_permissions():
    logger.info("Starting permission assignment")

    admins, _ = Group.objects.get_or_create(name="Admins")
    editors, _ = Group.objects.get_or_create(name="Editors")
    readonly, _ = Group.objects.get_or_create(name="Read Only")

    logger.info("Groups ensured: Admins, Editors, Read Only")
    # Permissions for Admins
    admin_perms = [
        "add_lists",
        "change_lists",
        "delete_lists",
        "view_lists",
        "add_items",
        "change_items",
        "delete_items",
        "view_items",
        "view_my_profile",
        "edit_my_profile",
    ]

    # Permissions for Editors
    editor_perms = [
        "view_lists",
        "change_lists",
        "view_items",
        "change_items",
    ]

    # Permissions for Read Only
    readonly_perms = [
        "view_lists",
        "view_items",
        "view_my_profile",
    ]

    # Helper to assign permissions safely
    def add_perms(group, perm_list):
        for codename in perm_list:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.add(perm)
                logger.info(f"Assigned {codename} to {group.name}")
            except Permission.DoesNotExist:
                print(f"Permission '{codename}' not found.")
                logger.warning(f"Permission '{codename}' not found")

    add_perms(admins, admin_perms)
    add_perms(editors, editor_perms)
    add_perms(readonly, readonly_perms)

    logger.info("Permission assignment complete")
