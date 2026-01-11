#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
dev.py


"""
__version__ = "0.0.0.000006-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-09 22:40:21"
###############################################################################

# WSGI_REQUEST_HANDLER = "MikesLists.logging.request_handler.RequestHandlerWithIPAndUser"

# WSGI_SERVER_CLASS = "MikesLists.logging.custom_server.CustomWSGIServer"
# WSGI_REQUEST_HANDLER = "MikesLists.logging.custom_server.RequestHandlerWithIPAndUser"

from .core import *

EXTRA_ALLOWED_HOSTS = []

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "MikesLists.context_processors.env_name"
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # -------------------------
    # FORMATTERS
    # -------------------------
    "formatters": {
        "pretty_sql": {
            "()": "MikesLists.logging.logging_formatters.PrettySQLFormatter",
            "format": "\n[SQL] {sql}\n[Time] {duration} ms\n",
            "style": "{",
        },
        "request_line": {
            # The custom handler injects: IP + username + message
            "format": "[REQ] {message}",
            "style": "{",
        },
    },

    # -------------------------
    # FILTERS
    # -------------------------
    "filters": {
        "ignore_bad_request_version": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: "Bad request version" not in record.getMessage(),
        },
        "ignore_https_warning": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: "You're accessing the development server over HTTPS"
            not in record.getMessage(),
        },
    },

    # -------------------------
    # HANDLERS
    # -------------------------
    "handlers": {
        "sql_file": {
            "class": "logging.FileHandler",
            "filename": "/srv/django/logs/sql.log",
            "formatter": "pretty_sql",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "pretty_sql",
        },
        "request_file": {
            "class": "logging.FileHandler",
            "filename": "/srv/django/logs/requests.log",
            "formatter": "request_line",
            "filters": [
                "ignore_bad_request_version",
                "ignore_https_warning",
            ],
        },
    },

    # -------------------------
    # LOGGERS
    # -------------------------
    "loggers": {
        "django.db.backends": {
            "handlers": ["console", "sql_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["request_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# WSGI_REQUEST_HANDLER = "MikesLists.logging.request_handler.RequestHandlerWithIP"

# WSGI_SERVER_CLASS = "MikesLists.logging.custom_server.CustomWSGIServer"
# WSGI_REQUEST_HANDLER = "MikesLists.logging.custom_server.RequestHandlerWithIPAndUser"
