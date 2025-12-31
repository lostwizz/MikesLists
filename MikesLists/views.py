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
__version__ = "0.0.3.00354-dev"
__author__ = "Mike Merrett"
__updated__ = "2025-12-24 22:12:27"
###############################################################################


import os

def home_view(request):
    # Get the settings string (e.g., 'MikesLists.settings.live')
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'dev')

    # Clean it up to just get 'live', 'test', or 'dev'
    env_name = settings_module.split('.')[-1]

    context = {
        'env_name': env_name.upper(),
    }
    return render(request, 'home.html', context)