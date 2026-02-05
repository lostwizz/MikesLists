#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
live.py
app_core.settings.live
/srv/django/MikesLists_dev/app_core/settings/live.py


"""
__version__ = "0.0.0.000076-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-05 15:14:23"
###############################################################################


from .core import *  # noqa: F403

# EXTRA_ALLOWED_HOSTS += []

# TEMPLATES[0]["OPTIONS"]["context_processors"].append(
#     "MikesLists.context_processors.env_name"
# )


LOGGING["handlers"]["console"]["level"] = "WARNING"
LOGGING["handlers"]["console"]["filters"] = ["exclude_debug_and_success"]
LOGGING["loggers"]["django.db.backends"]["level"] = "WARNING"
LOGGING["root"]["level"] = "INFO"
# LOGGING["handlers"]["app_file"]["filename"] = "/srv/django/logs_live/app.log"
LOGGING["handlers"]["app_file"]["filename"] = "/srv/django/logs/app_live.log"
LOGGING["handlers"]["sql_file"]["filename"] = "/srv/django/logs/sql_live.log"
LOGGING["handlers"]["request_file"]["filename"] = "/srv/django/logs/requests_live.log"
