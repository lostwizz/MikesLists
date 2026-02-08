#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
dev.py
settings.dev
/srv/django/MikesLists_dev/settings/dev.py



"""
__version__ = "0.0.0.000026-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-07 20:23:46"
###############################################################################

# WSGI_REQUEST_HANDLER = "app_core.logging.request_handler.RequestHandlerWithIPAndUser"

# WSGI_SERVER_CLASS = "app_core.logging.custom_server.CustomWSGIServer"
# WSGI_REQUEST_HANDLER = "app_core.logging.custom_server.RequestHandlerWithIPAndUser"

import socket

from .core import *  # noqa: F403

# INSTALLED_APPS.append('rest_framework')
# INSTALLED_APPS.append('rest_framework.authtoken')



INSTALLED_APPS.append("django_extensions")
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.TokenAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ],
# }


MIDDLEWARE += [
    "app_core.views.debug.DebugViewMiddleware",
]


# TEMPLATES[0]["OPTIONS"]["context_processors"].append(  # noqa: F405
#     "app_core.context_processors.env_name"
# )


AUTH_PASSWORD_VALIDATORS = []  # This disables all checks (NOT for production!)


# WSGI_REQUEST_HANDLER = "app_core.logging.request_handler.RequestHandlerWithIP"

# WSGI_SERVER_CLASS = "app_core.logging.custom_server.CustomWSGIServer"
# WSGI_REQUEST_HANDLER = "app_core.logging.custom_server.RequestHandlerWithIPAndUser"


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


HOSTNAME = socket.gethostname()
LOCAL_IP = get_local_ip()

# print(f"{HOSTNAME=}")
# print(f"{LOCAL_IP=}")

CSRF_TRUSTED_ORIGINS = [
    f"http://{HOSTNAME}",
    f"http://{HOSTNAME}.local",
    f"http://{LOCAL_IP}",
    "http://*.local",
]

LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["handlers"]["app_file"]["level"] = "DEBUG"      # Fixes app.log
LOGGING["handlers"]["sql_file"]["level"] = "DEBUG"      # Fixes sql.log
LOGGING["handlers"]["request_file"]["level"] = "DEBUG"  # Fixes requests.log

LOGGING["handlers"]["console"]["filters"] = []
LOGGING["loggers"]["django.db.backends"]["level"] = "DEBUG"
LOGGING["root"]["level"] = "DEBUG"

LOGGING["handlers"]["app_file"]["filename"] = "/srv/django/logs/app_dev.log"
LOGGING["handlers"]["sql_file"]["filename"] = "/srv/django/logs/sql_dev.log"
LOGGING["handlers"]["request_file"]["filename"] = "/srv/django/logs/requests_dev.log"
