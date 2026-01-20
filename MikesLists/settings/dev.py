#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
dev.py
MikesLists.settings.dev
/srv/django/MikesLists_dev/MikesLists/settings/dev.py

"""
__version__ = "0.0.0.000006-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 20:51:47"
###############################################################################

# WSGI_REQUEST_HANDLER = "MikesLists.logging.request_handler.RequestHandlerWithIPAndUser"

# WSGI_SERVER_CLASS = "MikesLists.logging.custom_server.CustomWSGIServer"
# WSGI_REQUEST_HANDLER = "MikesLists.logging.custom_server.RequestHandlerWithIPAndUser"

from .core import *  # noqa: F403

EXTRA_ALLOWED_HOSTS = []

# TEMPLATES[0]["OPTIONS"]["context_processors"].append(  # noqa: F405
#     "MikesLists.context_processors.env_name"
# )


AUTH_PASSWORD_VALIDATORS = []  # This disables all checks (NOT for production!)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,


    # -------------------------------------------------
    # ROOT LOGGER (THIS MAKES logging.debug() WORK)
    # -------------------------------------------------
    "root": {
        "handlers": ["console","app_file"],
        "level": "DEBUG",
    },

    # -------------------------
    # FORMATTERS
    # -------------------------
    "formatters": {
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
        "color": {
            "()": "MikesLists.logging.color_formatter.ColorFormatter",
            "format": "[{levelname}] {message}",
            "style": "{",
        },


        "pretty_sql": {
            "()": "MikesLists.logging.logging_formatters.PrettySQLFormatter",
            "format": "\n[SQL]\n{sql}\n[Time] {duration} ms\n",  # Added a newline after [SQL]
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
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "color",
        },
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/srv/django/logs/app.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "formatter": "simple",
        },

        # Optional SQL log file
        "sql_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/srv/django/logs/sql.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "pretty_sql",
        },

        "request_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/srv/django/logs/requests.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
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
        "mikeslists": {
            "handlers": ["app_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "ToDo": {
            "handlers": ["app_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["app_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },


        "django.db.backends": {
            # "handlers": ["console", "sql_file"],
            "handlers": ["sql_file"],
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
