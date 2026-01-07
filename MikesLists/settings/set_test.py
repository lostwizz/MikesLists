#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test.py


# TODO:
# COMMENT:
# NOTE:
# USEFULL:
# LEARN:
# RECHECK:
# INCOMPLETE:
# SEE NOTES:
# POST
# HACK

"""
__version__ = "0.0.0.000007-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-03 22:25:49"
###############################################################################

from .core import *

ALLOWED_HOSTS = ['localhost', 'localhost.local','127.0.0.1',
                 '10.0.0.208', 'pi204.local',
                 '10.0.0.156', 'pi156.local',
                 '10.0.0.100']


TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'MikesLists.context_processors.env_name'
)
