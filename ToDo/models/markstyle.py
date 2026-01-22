#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
typeflag.py
ToDo.models.typeflag
/srv/django/MikesLists_dev/ToDo/models/typeflag.py


"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-21 18:08:26"
###############################################################################

from django.db import models


# =================================================================
# for a user the USERSCOPE is any item avaiable to the user uses the same Checkmark
# for the timeUSER - for the user the time period expires the mark is removed  (all user lists  with that item will be timedout)
# for the timeLIST - for a user and a list if the time expires then it is rmoved - for the user it each separate list having the item will timeout individually)
# for the TheListScope - two separate list will have differnt result
# for the itmmScope - each item (notmater the lists) will have itsown mark - so a list could have the same item twice and set to itemscope - one does not affect the other
#
# =================================================================
class MarkStyle(models.TextChoices):
    """
    Format: NAME = 'VALUE', 'Label'
    """
    USERSCOPE = 'user', 'User Scope'
    TIMESCOPEUSER = 'timeUSER', 'Time Limits Scope'
    TIMESCOPELIST = 'timeLIST', 'Time Limits Scope'
    THELISTSCOPE = 'thelist', 'List Scope'
    ITEMSCOPE = 'theitem', 'Item Scope'
    #GLOBALSCOPE = 'global', 'Global Scope0'
