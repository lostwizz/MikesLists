#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py

    ToDo app's urls.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-17 00:53:33"
###############################################################################

from django.urls import path

from . import views   # This now works because __init__.py imported everything

urlpatterns = [
    # Example: empty path for the main list view
    # path('', views.todo_list, name='todo_list'),
    # path('', views.todo_item, name='todo_item'),
    path('', views.list_dashboard, name='dashboard'),
    # path('items/', views.item_views.todo_item, name='todo_items'),
    # path('item/<int:item_id>/toggle/', views.item_toggle_status, name='item_toggle_status'),
    path('', views.list_dashboard, name='dashboard'),
    path('items/', views.todo_item, name='todo_items'),
]


