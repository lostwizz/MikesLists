#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
markers.py
ToDo.models.markers
/srv/django/MikesLists_dev/ToDo/models/markers.py

"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-21 20:37:34"
###############################################################################


#########################################################################

import re
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

from .lists import Lists
from .items import Items
from .typeflag import TypeFlags
from .itemstatus import ItemStatus
from .markstyle import MarkStyle


# =================================================================
# =================================================================
class Markers(models.Model):

    list_obj = models.ForeignKey(Lists, on_delete=models.SET_NULL, null=True, blank=True, related_name="list_markers")

    item_obj= models.ForeignKey(Items, on_delete=models.SET_NULL, null=True, blank=True, related_name="item_markers")

    user_obj = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_markers")

    markervalue = models.CharField(500, blank=True, null=True, default=None )
    markerDateTime = models.DateTimeField(auto_now=True)

    markerStartTime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Marker"
        verbose_name_plural = "Markers"



    # -----------------------------------------------------------------
    def __str__(self):
        user = self.user_obj.username if self.user_obj else "NoUser"
        listname = self.list_obj.title if self.list_obj else "NoList"
        itemname = self.item_obj.title if self.item_obj else "NoItem"
        return f"{user} {listname} {itemname} ++> {self.markervalue}"
