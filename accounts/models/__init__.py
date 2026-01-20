#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
__init__.py
accounts.models
/srv/django/MikesLists_dev/accounts/models/__init__.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 22:06:52"
###############################################################################


from .profile import Profile
from .signals import create_user_profile, save_user_profile
