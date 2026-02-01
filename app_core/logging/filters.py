#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
filters.py
app_core.logging.filters
/srv/django/MikesLists_dev/app_core/logging/filters.py





"""
__version__ = "0.0.0.000012-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-31 23:45:31"
##############################################################################
import logging

# =================================================================
class ExcludeLevelFilter(logging.Filter):
    """
    Filter that excludes specific log levels.
    """

    # -----------------------------------------------------------------
    def __init__(self, levels_to_exclude=None):
        super().__init__()
        self.levels_to_exclude = levels_to_exclude or []

    # -----------------------------------------------------------------
    def filter(self, record):
        # Return False to exclude the record, True to keep it
        return record.levelname not in self.levels_to_exclude
