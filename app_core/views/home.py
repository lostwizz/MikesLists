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
__updated__ = "2026-01-28 21:45:32"
###############################################################################

from django.conf import settings
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required


def redirect_root_to_dashboard(request):
    return redirect("accounts:dashboard")

def redirect_home_to_dashboard(request):
    return redirect("accounts:dashboard")

def redirect_accounts_to_dashboard(request):
    return redirect("accounts:dashboard")

def redirect_dashboard_to_dashboard(request):
    return redirect("accounts:dashboard")

def catchall_redirect(request, path=None):
    return redirect("accounts:dashboard")




def home(request):
    env_name = settings.ENV_NAME
    return render(request, "app_core.home.html", {"env": env_name})
