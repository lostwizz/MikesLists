#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
profile.py
app_accounts.views.group_manager
/srv/django/MikesLists_dev/app_accounts/views/group_manager.py





"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:06:12"
###############################################################################

from django.contrib.auth.models import Group, Permission
from django.shortcuts import render, redirect

def group_manager(request):
    groups = Group.objects.all()
    permissions = Permission.objects.all()

    if request.method == "POST":
        group_id = request.POST.get("group_id")
        perm_ids = request.POST.getlist("permissions")

        group = Group.objects.get(id=group_id)
        group.permissions.set(perm_ids)

        return redirect("group_manager")

    return render(request, "app_accounts/group_manager.html", {
        "groups": groups,
        "permissions": permissions,
    })
