#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
home.py


# TODO:
# COMMENT:
# NOTE:
# USEFULL:
# LEARN:
# RECHECK:
# INCOMPLETE:
# SEE NOTES:
# POST
# HACK

"""
__version__ = "0.0.0.00003-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-02 19:49:31"
###############################################################################

from django.conf import settings
from django.shortcuts import render

def home(request):
    env_name = settings.ENV_NAME  # You define this in each settings file
    return render(request, 'home.html', {"env_name": env_name})
