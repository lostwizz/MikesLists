#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
color_formatter.py
app_core.logging.color_formatter
/srv/django/MikesLists_dev/app_core/logging/color_formatter.py




"""
__version__ = "0.0.0.000014-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-05 17:09:29"
###############################################################################
# app_core/logging/color_formatter.py
import logging
from app_core.logging.constants import CUSTOM_LOG_LEVELS


# =================================================================
# =================================================================
class ColorFormatter(logging.Formatter):
    BASE_COLORS = {
        "DEBUG": "\x1b[36m",
        "INFO": "\x1b[32m",
        "WARNING": "\x1b[33m",
        "ERROR": "\x1b[31m",
        "CRITICAL": "\x1b[1;31m",
    }
    RESET = "\x1b[0m"

    # -----------------------------------------------------------------
    def format(self, record):
        # 1. Get Color and Prefix
        # mapping: { "LEVELNAME": (color, prefix) }
        config_map = {name: (val[1], val[2]) for name, val in CUSTOM_LOG_LEVELS.items()}

        color, prefix = config_map.get(record.levelname, (self.BASE_COLORS.get(record.levelname, self.RESET), ""))

        # 2. Add prefix to the message if it exists
        if prefix:
            record.msg = f"{prefix} {record.msg}"

        # 3. Format with color
        message = super().format(record)
        return f"{color}{message}{self.RESET}"
