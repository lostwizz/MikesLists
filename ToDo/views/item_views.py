#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
item_views.py
ToDo.views.item_views
/srv/django/MikesLists_dev/ToDo/views/item_views.py


Item CRUD views for the ToDo app.




"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 11:21:13"

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from accounts.utils.roles import require_group

from ToDo.models.items import Items
from ToDo.models.lists import Lists
from ToDo.forms.item_forms import ItemForm
from ToDo.models.itemstatus import ItemStatus


# ---------------------------------------------------------------------
# LIST ALL ITEMS FOR CURRENT USER
# ---------------------------------------------------------------------
@require_group("Admins", "Editors", "Read Only")
def todo_item_list(request):
    items = Items.objects.filter(created_user=request.user).order_by("-created_at")
    return render(request, "ToDo/items.html", {"items": items})


# ---------------------------------------------------------------------
# ITEM DETAIL VIEW
# ---------------------------------------------------------------------
@require_group("Admins", "Editors", "Read Only")
def todo_item_detail(request, pk):
    item = get_object_or_404(Items, pk=pk, created_user=request.user)
    return render(request, "ToDo/item_row.html", {"item": item})


# ---------------------------------------------------------------------
# CREATE NEW ITEM
# ---------------------------------------------------------------------
@require_group("Admins", "Editors")
def todo_item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_user = request.user
            item.save()
            return redirect("todo:todo_items")
    else:
        form = ItemForm()

    return render(request, "ToDo/item_form.html", {"form": form})


# ---------------------------------------------------------------------
# EDIT EXISTING ITEM
# ---------------------------------------------------------------------
@require_group("Admins", "Editors")
def todo_item_edit(request, pk):
    item = get_object_or_404(Items, pk=pk, created_user=request.user)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("todo:todo_items")
    else:
        form = ItemForm(instance=item)

    return render(request, "ToDo/item_form.html", {"form": form, "item": item})


# ---------------------------------------------------------------------
# DELETE ITEM
# ---------------------------------------------------------------------
@require_group("Admins")
def todo_item_delete(request, pk):
    item = get_object_or_404(Items, pk=pk, created_user=request.user)
    item.delete()
    return redirect("todo:todo_items")


# ---------------------------------------------------------------------
# TOGGLE STATUS (HTMX + fallback)
# ---------------------------------------------------------------------
@require_group("Admins", "Editors")
def item_toggle_status(request, item_id):
    item = get_object_or_404(Items, id=item_id, created_user=request.user)

    # Toggle logic
    item.status = (
        ItemStatus.COMPLETED
        if item.status == ItemStatus.PENDING
        else ItemStatus.PENDING
    )
    item.save()

    # HTMX partial update
    if request.headers.get("HX-Request"):
        return render(request, "ToDo/partials/item_row.html", {"item": item})

    # Standard redirect
    return redirect(request.META.get("HTTP_REFERER", "todo:todo_items"))
