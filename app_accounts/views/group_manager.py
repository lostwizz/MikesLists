#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
profile.py
app_accounts.views.group_manager
/srv/django/MikesLists_dev/app_accounts/views/group_manager.py


    The `group_manager_view` function in this Django app allows only users in the 'Admins' group to
    manage user roles by assigning or clearing roles for users.

    :param request: The `request` parameter in Django represents the HTTP request that triggered the
    view. It contains information about the request, such as the user making the request, any data sent
    with the request, and other metadata. The view uses this parameter to access information about the
    current request and to interact with the Django
    :return: The `group_manager_view` function returns a rendered HTML template named
    "group_manager.html" along with the context data containing the users and all groups fetched from
    the database. This function is decorated with `@group_required('Admins')`, which ensures that only
    users in the 'Admins' group can access this view. The function handles both GET and POST requests,
    where POST requests involve assigning roles



"""
__version__ = "0.0.0.000018-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-14 01:34:07"
###############################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# Import your new utilities
from app_accounts.utils.roles import assign_role_to_user
from app_accounts.utils.decorators import group_required  # Import your tool


User = get_user_model()

@group_required('Admins')  # Only users in the 'Admins' group can enter
def group_manager_view(request):
    # GET Logic: Fetch data for the template
    users = User.objects.all().prefetch_related('groups')
    all_groups = Group.objects.all()

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role_name = request.POST.get("role_name")
        action = request.POST.get("action")  # e.g., 'assign' or 'clear'

        target_user = get_object_or_404(User, id=user_id)

        if action == "assign":
            if assign_role_to_user(target_user, role_name):
                messages.success(request, f"Updated {target_user.username} to {role_name}.")
            else:
                messages.error(request, "Role update failed.")

        elif action == "clear_all":
            target_user.groups.clear()
            messages.info(request, f"Removed all roles from {target_user.username}.")

        return redirect("accounts:group_manager")



    context = {
        "users": users,
        "all_groups": all_groups,
    }
    return render(request, "app_accounts/group_manager.html", context)
