#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
conftest.py
conftest
/srv/django/MikesLists_dev/app_core/tests/logging/conftest.py


"""
__version__ = "0.0.0.000044-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-11 21:19:22"
###############################################################################


import logging
import pytest

@pytest.fixture
def logger():
    return logging.getLogger("test_logger")
