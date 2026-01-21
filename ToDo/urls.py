#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py
ToDo.urls
/srv/django/MikesLists_dev/ToDo/urls.py

    ToDo app's urls.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 11:05:01"
###############################################################################

from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('', views.list_dashboard, name='list_dashboard'),
    path('items/', views.todo_item_list, name='todo_items'),
    path('item/<int:pk>/', views.todo_item_detail, name='todo_item_detail'),
    path('item/new/', views.todo_item_create, name='todo_item_create'),
    path('item/<int:pk>/edit/', views.todo_item_edit, name='todo_item_edit'),
    path('item/<int:pk>/delete/', views.todo_item_delete, name='todo_item_delete'),
]
