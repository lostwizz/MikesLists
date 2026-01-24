#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
itemstatus.py
from app_ToDo.models.itemstatus import /srv/django/MikesLists_dev/ToDo/models/itemstatus.py
/srv/django/MikesLists_dev/app_ToDo/models/itemstatus.py


"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:16:52"
###############################################################################

from django.db import models


# =================================================================
# =================================================================
class ItemStatus(models.TextChoices):
    """
    Format: NAME = 'VALUE', 'Label'
    """

    ACTIVE = "ACTIVE", "Active"
    UNKNOWN = "UNKNOWN", "Unknown"
    COMPLETE = "COMPLETE", "Complete"
    INCOMPLETE = "INCOMPLETE", "Incomplete"
    POSTPONED = "POSTPONED", "Postponed"
    DROPPED = "DROPPED", "Dropped"
    PARTIALLY_COMPLETE = "PARTIALLY_COMPLETE", "Partially Complete"
