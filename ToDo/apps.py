#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
apps.py



"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-16 20:30:06"
###############################################################################

from django.apps import AppConfig


# =================================================================
# =================================================================
class TodoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ToDo'
