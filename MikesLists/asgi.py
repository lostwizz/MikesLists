#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
asgi.py
MikesLists.asgi
/srv/django/MikesLists_dev/MikesLists/asgi.py


"""
__version__ = "0.0.0.000004-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 20:46:13"
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
