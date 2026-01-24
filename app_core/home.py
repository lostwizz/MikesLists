#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
home.py
app_core.home
/srv/django/MikesLists_dev/app_core/home.py


"""
__version__ = "0.0.0.000004-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:11:29"
###############################################################################

from django.conf import settings
from django.shortcuts import render


def home(request):
    env_name = settings.ENV_NAME
    return render(request, "home.html", {"env": env_name})
