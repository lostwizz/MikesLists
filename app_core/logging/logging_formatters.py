#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
logging_formatters.py
app_core.logging.logging_formatters
/srv/django/MikesLists_dev/app_core/logging/logging_formatters.py



"""
__version__ = "0.0.0.000077-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-11 21:35:25"
###############################################################################

import logging
import sqlparse
import re


# -----------------------------------------------------------------
class PrettySQLFormatter(logging.Formatter):
    """
    A predictable, testable SQL formatter.

    For CREATE TABLE:
    - We fully control the formatting.
    - We split columns ourselves.
    - We guarantee lines that begin with:
        `...`
        PRIMARY ...
        CONSTRAINT ...
    - We guarantee a standalone ')'
    """

    def format(self, record):
        raw_sql = getattr(record, "sql", record.getMessage())
        duration = getattr(record, "duration", "0.0")

        clean_sql = " ".join(raw_sql.split())

        # ---------------------------------------------------------
        # CUSTOM CREATE TABLE HANDLING (fully deterministic)
        # ---------------------------------------------------------
        if clean_sql.upper().startswith("CREATE TABLE"):
            before_paren, after_paren = clean_sql.split("(", 1)
            columns_block, after_block = after_paren.rsplit(")", 1)

            # Split columns by comma
            columns = [col.strip() for col in columns_block.split(",")]

            # Build predictable multi-line SQL
            lines = []
            lines.append(before_paren.strip() + " (")
            for col in columns:
                lines.append(col)  # raw column line
            lines.append(")")
            clean_sql = "\n".join(lines)

        # ---------------------------------------------------------
        # Apply your custom indentation rules
        # ---------------------------------------------------------
        final_lines = []
        for line in clean_sql.splitlines():
            stripped = line.lstrip()
            if not stripped:
                continue

            if (
                stripped.startswith("`")
                or stripped.startswith("PRIMARY")
                or stripped.startswith("CONSTRAINT")
            ):
                final_lines.append("    " + stripped)

            elif stripped == ")":
                final_lines.append(stripped)

            else:
                final_lines.append(stripped)

        record.sql = "\n".join(final_lines)
        record.duration = duration

        return super().format(record)
