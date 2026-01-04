#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
wsgi.py


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
__updated__ = "2026-01-02 19:50:21"
###############################################################################

"""
WSGI config for MikesLists project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

##os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MikesLists.settings.dev')
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    cwd = os.getcwd()
    if 'live' in cwd:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'MikesLists.settings.live'
    elif 'test' in cwd:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'MikesLists.settings.test'
    else:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'MikesLists.settings.dev'
application = get_wsgi_application()
