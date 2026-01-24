#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
typeflag.py
app_ToDo.models.typeflag
/srv/django/MikesLists_dev/app_ToDo/models/typeflag.py



"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:17:36"
###############################################################################

from django.db import models


# =================================================================
# =================================================================
class TypeFlags(models.TextChoices):
    """
    Format: NAME = 'VALUE', 'Label'
    """
    CHECKMARK = 'CHECKMARK', 'Checkmark'
    RADIO = 'RADIO', 'Radio Buttons'
    MULTICHOICE = 'MULTICHOICE', 'Multi-Choice'
    HYPERLINK = 'HYPERLINK', 'Hyperlink'
