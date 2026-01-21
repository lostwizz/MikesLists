#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
list_views.py
ToDo.views.list_views
/srv/django/MikesLists_dev/ToDo/views/list_views.py

List dashboard + List CRUD views for the ToDo app.




"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 11:21:52"
###############################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.utils.roles import require_group

from ToDo.models.lists import Lists
from ToDo.models.items import Items
from ToDo.forms.item_forms import ItemForm   # used for inline item creation


# ---------------------------------------------------------------------
# LIST DASHBOARD (shows all items for the current user)
# ---------------------------------------------------------------------
@require_group("Admins", "Editors", "Read Only")
def list_dashboard(request):
    """
    The main ToDo dashboard.
    Shows all items created by the current user.
    """
    items = Items.objects.filter(created_user=request.user).order_by("-created_at")
    return render(request, "ToDo/lists.html", {"items": items})


# ---------------------------------------------------------------------
# LIST ALL LISTS (admin/editor only)
# ---------------------------------------------------------------------
@require_group("Admins", "Editors")
def list_all(request):
    """
    Shows all lists (not items). Useful for managing list containers.
    """
    lists = Lists.objects.filter(created_user=request.user).order_by("-created_at")
    return render(request, "ToDo/lists.html", {"lists": lists})


# ---------------------------------------------------------------------
# LIST DETAIL VIEW (shows items inside a specific list)
# ---------------------------------------------------------------------
@require_group("Admins", "Editors", "Read Only")
def list_detail(request, pk):
    todo_list = get_object_or_404(Lists, pk=pk, created_user=request.user)
    items = Items.objects.filter(list=todo_list).order_by("-created_at")

    return render(
        request,
        "ToDo/lists.html",
        {"list": todo_list, "items": items},
    )


# ---------------------------------------------------------------------
# CREATE NEW LIST
# ---------------------------------------------------------------------
@require_group("Admins", "Editors")
def list_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if not name:
            messages.error(request, "List name cannot be empty.")
        else:
            Lists.objects.create(name=name, created_user=request.user)
            messages.success(request, "List created successfully.")
            return redirect("todo:list_dashboard")

    return render(request, "ToDo/list_form.html")


# ---------------------------------------------------------------------
# EDIT EXISTING LIST
# ---------------------------------------------------------------------
@require_group("Admins", "Editors")
def list_edit(request, pk):
    todo_list = get_object_or_404(Lists, pk=pk, created_user=request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        if not name:
            messages.error(request, "List name cannot be empty.")
        else:
            todo_list.name = name
            todo_list.save()
            messages.success(request, "List updated successfully.")
            return redirect("todo:list_dashboard")

    return render(request, "ToDo/list_form.html", {"list": todo_list})


# ---------------------------------------------------------------------
# DELETE LIST
# ---------------------------------------------------------------------
@require_group("Admins")
def list_delete(request, pk):
    todo_list = get_object_or_404(Lists, pk=pk, created_user=request.user)
    todo_list.delete()
    messages.success(request, "List deleted successfully.")
    return redirect("todo:list_dashboard")

