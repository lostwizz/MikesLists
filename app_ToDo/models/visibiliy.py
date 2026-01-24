#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
visibiliy.py
app_ToDo.models.visibiliy
/srv/django/MikesLists_dev/app_ToDo/models/visibiliy.py


"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:17:42"
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
    GLOBAL = 'global', 'Global Visibility'
    USER = 'user', 'User Visibility'
    GROUPS = 'group', 'Group(s) Visibility'
