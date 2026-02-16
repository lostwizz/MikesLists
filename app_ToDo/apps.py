#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
apps.py
app_ToDo.apps
/srv/django/MikesLists_dev/app_ToDo/apps.py



"""
__version__ = "0.0.1.000003-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-15 17:26:04"
###############################################################################

# /srv/django/MikesLists_dev/app_ToDo/apps.py
from django.apps import AppConfig
class AppTodoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_ToDo"

    def ready(self):
        # No permission logic here
        pass
