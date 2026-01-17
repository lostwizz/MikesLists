#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
typeflag.py


"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-16 21:24:53"
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
