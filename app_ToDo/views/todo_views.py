#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
views.py
app_ToDo.views.views
/srv/django/MikesLists_dev/app_ToDo/views/views.py


"""
__version__ = "0.0.0.000015-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 17:10:32"
###############################################################################
from django.shortcuts import render

def todo_list(request):  # <--- Make sure this name matches exactly
    # Your logic here
    return render(request, 'app_ToDo/todo_list.html')
