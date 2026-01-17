#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test.py


"""
__version__ = "0.0.0.000060-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-14 22:06:01"
###############################################################################

from .core import *  # noqa: F403

# EXTRA_ALLOWED_HOSTS += []

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "MikesLists.context_processors.env_name"
)
