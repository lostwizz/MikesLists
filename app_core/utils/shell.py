#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
shell.py
app_core.utils.shell
/srv/django/MikesLists_dev/app_core/utils/shell.py




"""
__version__ = "0.1.0.000026-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 21:56:39"
###############################################################################

import subprocess

def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
