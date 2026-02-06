#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
decorators.py
app_core.utils.decorators
/srv/django/MikesLists_dev/app_core/utils/decorators.py




# Optional: Custom permission/group decorators


"""
__version__ = "0.0.0.000026-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-05 21:33:54"
###############################################################################

from django.conf import settings
from django.http import HttpResponseForbidden
from functools import wraps
from app_core.utils.env import is_dev, get_env

# -----------------------------------------------------------------
def dev_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the environment is 'dev'
        if is_dev():
            return HttpResponseForbidden("This view is only available in the development environment.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# -----------------------------------------------------------------
def testlive_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the environment is 'dev'
        if not is_dev():
            return HttpResponseForbidden("This view is only available in the test and live environment.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
