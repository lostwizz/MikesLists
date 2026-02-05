#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test.py
app_core.settings.test
/srv/django/MikesLists_dev/app_core/settings/test.py


"""
__version__ = "0.0.0.000072-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-05 15:16:50"
###############################################################################

from .core import *  # noqa: F403

MIDDLEWARE += [
    "app_core.views.debug.DebugViewMiddleware",
]

# EXTRA_ALLOWED_HOSTS += []

# TEMPLATES[0]["OPTIONS"]["context_processors"].append(
#     "app_core.context_processors.env_name"
# )


LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["handlers"]["console"]["filters"] = []
LOGGING["handlers"]["app_file"]["level"] = "CRITICAL"
LOGGING["handlers"]["sql_file"]["level"] = "CRITICAL"
LOGGING["handlers"]["request_file"]["level"] = "CRITICAL"
LOGGING["loggers"]["django.db.backends"]["level"] = "WARNING"
LOGGING["root"]["level"] = "DEBUG"

LOGGING["handlers"]["app_file"]["filename"] = "/srv/django/logs/app_test.log"
LOGGING["handlers"]["sql_file"]["filename"] = "/srv/django/logs/sql_test.log"
LOGGING["handlers"]["request_file"]["filename"] = "/srv/django/logs/requests_test.log"
