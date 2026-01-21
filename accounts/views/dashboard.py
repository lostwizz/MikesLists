#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
dashboard.py
accounts.views.dashboard
/srv/django/MikesLists_dev/accounts/views/dashboard.py

Dashboard view showing user statistics.


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 11:43:49"
###############################################################################


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ToDo.models.items import Items
from ToDo.models.lists import Lists


@login_required
def dashboard(request):
    """
    Dashboard showing:
    - Total items created by the user
    - Completed items
    - Total lists
    """

    total_items = Items.objects.count()
    completed_items = Items.objects.filter(completed=True).count()
    total_lists = Lists.objects.count()


    context = {
        "total_items": total_items,
        "completed_items": completed_items,
        "total_lists": total_lists,
    }

    return render(request, "accounts/dashboard_stats.html", context)
