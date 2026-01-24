#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py
app_ToDo.urls
/srv/django/MikesLists_dev/app_ToDo/urls.py


    ToDo app's urls.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 20:21:39"
###############################################################################

from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    # path('', views.list_dashboard, name='list_dashboard'),

    # # Change 'app_todo_items' to 'todo_items'
    # path('items/', views.todo_item_list, name='todo_items'),

    # # Do the same for the others if you want them to be easier to use in base.html
    # path('item/<int:pk>/', views.todo_item_detail, name='todo_item_detail'),
    # path('item/new/', views.todo_item_create, name='todo_item_create'),
    # path('item/<int:pk>/edit/', views.todo_item_edit, name='todo_item_edit'),
    # path('item/<int:pk>/delete/', views.todo_item_delete, name='todo_item_delete'),
]
