#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
shell.py
app_core.utils.shell
/srv/django/MikesLists_dev/app_core/utils/shell.py


Safe subprocess helpers for app_core.



__version__ = "0.1.0.000032-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-09 00:11:57"
"""
###############################################################################
from __future__ import annotations
import subprocess
from typing import List, Optional


# -----------------------------------------------------------------
def run(cmd: List[str], *, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """
    Safely run a command without invoking the shell.
    Example:
        run(["ls", "-la"])
    """
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )


# -----------------------------------------------------------------
def run_shell(cmd: str, *, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """
    Run a command using the shell.
    Explicitly unsafe unless needed.
    """
    return subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )


# -----------------------------------------------------------------
def run_checked(cmd: List[str], *, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """
    Run a command and raise CalledProcessError on failure.
    """
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=True,
    )

# -----------------------------------------------------------------
# -----------------------------------------------------------------
