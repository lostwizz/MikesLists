#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
dashboard.py
accounts.views.dashboard
/srv/django/MikesLists_dev/accounts/views/dashboard.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 00:14:19"
###############################################################################


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.utils.roles import get_user_role
from ToDo.models import Items, Lists



@login_required
def dashboard(request):
    role = get_user_role(request.user)

    items = Items.objects.all()
    lists = Lists.objects.all()

    if role == "admin":
        template = "dashboard/admin.html"
    elif role == "editor":
        template = "dashboard/editor.html"
    else:
        template = "dashboard/readonly.html"

    return render(request, template, {
        "items": items,
        "lists": lists,
        "role": role,
    })
