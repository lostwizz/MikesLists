#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test.py
app_core.settings.test
/srv/django/MikesLists_dev/app_core/settings/test.py


"""
__version__ = "0.0.0.000080-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 22:35:40"
###############################################################################

from .core import *  # noqa: F403


ADMIN_ALLOWED_IP_PREFIXES = [
    "10.0.0.",
    "127.0.0.1",
]


STATUS_ALLOW_RESTART = False
STATUS_RESTART_SCRIPT = "/home/pi/bin/bounce.sh"


MIDDLEWARE += [
    "app_core.views.debug.DebugViewMiddleware",
]

# EXTRA_ALLOWED_HOSTS += []

# TEMPLATES[0]["OPTIONS"]["context_processors"].append(
#     "app_core.context_processors.env_name"
# )


# LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["handlers"]["console"]["filters"] = []

LOGGING["handlers"]["app_file"]["level"] = "CRITICAL"
# LOGGING["handlers"]["app_file"]["level"] = "DEBUG"

LOGGING["handlers"]["sql_file"]["level"] = "CRITICAL"
# LOGGING["handlers"]["sql_file"]["level"] = "DEBUG"

LOGGING["handlers"]["request_file"]["level"] = "CRITICAL"
# LOGGING["handlers"]["request_file"]["level"] = "DEBUG"

LOGGING["loggers"]["django.db.backends"]["level"] = "WARNING"
# LOGGING["loggers"]["django.db.backends"]["level"] = "DEBUG"

LOGGING["root"]["level"] = "DEBUG"

LOGGING["handlers"]["app_file"]["filename"] =     "/srv/django/logs/app_test.log"
LOGGING["handlers"]["sql_file"]["filename"] =     "/srv/django/logs/sql_test.log"
LOGGING["handlers"]["request_file"]["filename"] = "/srv/django/logs/requests_test.log"
