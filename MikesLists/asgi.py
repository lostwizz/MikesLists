#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
asgi.py


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
__updated__ = "2026-01-02 19:51:24"
###############################################################################

"""
ASGI config for MikesLists project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MikesLists.settings')

application = get_asgi_application()
