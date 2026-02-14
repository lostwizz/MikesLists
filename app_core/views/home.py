#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
home.py
app_core.home
/srv/django/MikesLists_dev/app_core/home.py


"""
__version__ = "0.0.0.000006-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-12 22:31:05"
###############################################################################

from django.conf import settings
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from app_core.utils.env import is_dev, get_env


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
    return render(request, "app_core/home.html", {"env": get_env()})
