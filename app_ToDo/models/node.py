#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
node.py
app_ToDo.models.node
/srv/django/MikesLists_dev/app_ToDo/models/node.py





"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 23:07:04"
###############################################################################


from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class Node(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=25)
    is_completed = models.BooleanField(default=False)
    user_obj = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_markers")
    visibility_allowed_groups = models.ManyToManyField(Group, blank=True)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
