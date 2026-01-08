#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
live.py


"""
__version__ = "0.0.0.000070-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-03 22:44:35"
###############################################################################


from .core import *

# EXTRA_ALLOWED_HOSTS += []

TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'MikesLists.context_processors.env_name'
)
