#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
list_views.py

for the lists this is the view


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-17 22:50:40"
###############################################################################


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.conf import settings
from decouple import config

from ToDo.models.lists import Lists


# -----------------------------------------------------------------


# -----------------------------------------------------------------
@login_required
def list_dashboard(request):
    # 1. Get the data from the database
    all_lists = Lists.objects.all()

    # 2. Define the context dictionary
    context = {
        "lists": all_lists,
        "env_name": getattr(settings, "ENV_NAME", "Development"),
    }

    # 3. Pass the context to the template
    # Make sure 'ToDo/lists.html' exists in ToDo/templates/ToDo/
    return render(request, "ToDo/lists.html", context)


# -----------------------------------------------------------------
def todo_list(request):
    lists = Lists.objects.all().order_by("-created_at")
    return render(request, "ToDo/lists.html", {"lists": lists})


# -----------------------------------------------------------------
def list_management(request):
    lists = Lists.objects.all()
    return render(request, "list_management.html", {"lists": lists})


# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
