#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
views.py


# TODO:
# COMMENT:
# NOTE:
# USEFULL:
# LEARN:
# RECHECK
# INCOMPLETE
# SEE NOTES
# POST
# HACK
# FIXME
# BUG
# [ ] something to do
# [x]  i did sometrhing



"""
__version__ = "0.0.0.00003-dev"
__author__ = "Mike Merrett"
__updated__ = "2025-12-24 22:12:27"
###############################################################################

from django.conf import settings
from django.shortcuts import render

def home(request):
    env_name = settings.ENV_NAME  # You define this in each settings file
    return render(request, 'home.html', {"env_name": env_name})
