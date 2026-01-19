#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
apps.py
ToDo.apps
/srv/django/MikesLists_dev/ToDo/apps.py


"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 20:38:47"
###############################################################################

from django.apps import AppConfig


# =================================================================
# =================================================================
class TodoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ToDo'
