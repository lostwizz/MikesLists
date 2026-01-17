#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
home.py


"""
__version__ = "0.0.0.000004-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-17 00:44:14"
###############################################################################

from django.conf import settings
from django.shortcuts import render

def home(request):
    env_name = settings.ENV_NAME  # You define this in each settings file
    return render(request, 'home.html', {"env_name": env_name})
