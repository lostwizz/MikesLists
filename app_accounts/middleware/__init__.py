#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
__init__.py
app_accounts.middleware
/srv/django/MikesLists_dev/app_accounts/middleware/__init__.py




"""
__version__ = "0.0.0.000013-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-14 22:50:39"
###############################################################################


# from .login_required_middleware import ActiveUserMiddleware, UpdateLastActivityMiddleware, LoginRequiredMiddleware
# from .login_required_middleware import UpdateLastActivityMiddleware, LoginRequiredMiddleware
from .login_required_middleware import LoginRequiredMiddleware
