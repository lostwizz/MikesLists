# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# ###############################################################################
# r"""
# markers.py
# app_ToDo.models.markers
# /srv/django/MikesLists_dev/app_ToDo/models/markers.py


# When a Marker is created:
#     m = Markers.objects.create(...)
#     m.markerStartTime   # → None

# When you want to set it later:
#     m.markerStartTime = timezone.now()
#     m.save()

# When you want to clear it again:
#     m.markerStartTime = None
#     m.save()



# """
# __version__ = "0.0.0.000011-dev"
# __author__ = "Mike Merrett"
# __updated__ = "2026-01-23 01:17:14"
# ###############################################################################


# #########################################################################

# import re
# from django.db import models

# # Create your models here.
# from django.contrib.auth.models import User
# from django.db import models

# from .lists import Lists
# from .items import Items
# from .typeflag import TypeFlags
# from .itemstatus import ItemStatus
# from .markstyle import MarkStyle


# # =================================================================
# # =================================================================
# class Markers(models.Model):

#     list_obj = models.ForeignKey(Lists, on_delete=models.SET_NULL, null=True, blank=True, related_name="list_markers")

#     item_obj= models.ForeignKey(Items, on_delete=models.SET_NULL, null=True, blank=True, related_name="item_markers")

#     user_obj = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_markers")

#     markervalue = models.CharField(max_length=500, blank=True, null=True, default=None )
#     markerDateTime = models.DateTimeField(null=True, blank=True, default=None)

#     markerStartTime = models.DateTimeField(null=True, blank=True, default=None)

#     class Meta:
#         verbose_name = "Marker"
#         verbose_name_plural = "Markers"



#     # -----------------------------------------------------------------
#     def __str__(self):
#         user = self.user_obj.username if self.user_obj else "NoUser"
#         listname = self.list_obj.title if self.list_obj else "NoList"
#         itemname = self.item_obj.title if self.item_obj else "NoItem"
#         return f"{user} {listname} {itemname} ++> {self.markervalue}"
