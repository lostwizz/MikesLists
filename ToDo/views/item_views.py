#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
item_views.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-17 17:01:31"
###############################################################################


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ToDo.models.items import Items
from ToDo.models.lists import Lists
from ToDo.forms.item_forms import ItemForm
from ToDo.models.itemstatus import ItemStatus  # Assuming your status Enum is here


# -----------------------------------------------------------------
def todo_item(request):
    items = Items.objects.all().order_by("-created_at")
    return render(request, "ToDo/items.html", {"items": items})


# -----------------------------------------------------------------
def item_management(request, list_id):
    # list = Lists.objects.get(id=list_id)
    # items = Items.objects.filter(list=list)
    # return render(request, 'item_management.html', {'list': list, 'items': items})
    todo_list = get_object_or_404(Lists, id=list_id)
    items = Items.objects.filter(list=todo_list)
    return render(
        request, "ToDo/item_management.html", {"list": todo_list, "items": items}
    )


# -----------------------------------------------------------------
@login_required
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            # Assign any extra logic here (like setting the user)
            item.created_user = request.user
            item.save()
            return redirect("dashboard")
    else:
        form = ItemForm()

    return render(request, "ToDo/item_form.html", {"form": form})


# -----------------------------------------------------------------
@login_required
def item_toggle_status(request, item_id):
    item = get_object_or_404(Items, id=item_id)

    # Toggle logic
    item.status = (
        ItemStatus.COMPLETED
        if item.status == ItemStatus.PENDING
        else ItemStatus.PENDING
    )
    item.save()

    # If it's an HTMX request, return only the row snippet
    if request.headers.get("HX-Request"):
        return render(request, "ToDo/partials/item_row.html", {"item": item})

    # Fallback for standard form submissions
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
