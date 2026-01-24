#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
wsgi.py
app_core.wsgi
/srv/django/MikesLists_dev/app_core/wsgi.py


"""
__version__ = "0.0.0.000004-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:14:39"
###############################################################################

"""
WSGI config for MikesLists project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

##os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_core.settings.dev')
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    cwd = os.getcwd()
    if 'live' in cwd:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'app_core.settings.live'
    elif 'test' in cwd:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'app_core.settings.test'
    else:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'app_core.settings.dev'
application = get_wsgi_application()
