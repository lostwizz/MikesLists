#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
health.py
app_core.logging.logging
/srv/django/MikesLists_dev/app_core/logging/logging.py


"""
__version__ = "0.0.0.000025-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-01 00:47:45"
###############################################################################


from django.apps import AppConfig


class AppCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_core'

    def ready(self):

        # This imports your logging setup and runs the initialization code
        from app_core.logging.logging import logger
        logger.warning("hello woprld- i am here")
