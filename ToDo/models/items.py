#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
items.py

    ToDo app's models.py



Since this is a structural change, you need to migrate:

        Generate Migration: python manage.py makemigrations ToDo --settings=MikesLists.settings.dev
        View the SQL (to see your linking table): python manage.py sqlmigrate ToDo [new_migration_number] --settings=MikesLists.settings.dev
        You will notice a new CREATE TABLE ToDo_lists_items ... in the pretty output!
        Apply Migration: python manage.py migrate ToDo --settings=MikesLists.settings.dev



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
# FIXME
# BUG
# [ ] something to do
# [x]  i did sometrhing

"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-17 00:22:56"
###############################################################################

import re
from django.db import models

# Create your models here.

from django.db import models

from .typeflag import TypeFlags
from .itemstatus import ItemStatus

# =================================================================
# =================================================================
class Items(models.Model):
    # id = bigint??????
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=30, default="v1.0")
    attachment = models.BinaryField(blank=True, null=True)  # upload_to='attachments/',

    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    payload = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ItemStatus.choices, default=ItemStatus.ACTIVE)
    created_user = models.CharField(max_length=100, blank=True, null=True)

    typeflag = models.CharField(
        max_length=20, choices=TypeFlags.choices, default=TypeFlags.CHECKMARK
    )

    # -----------------------------------------------------------------
    def __str__(self):
        # return self.title
        return f"{self.title} (v{self.version})"

    # =================================================================
    class Meta:
        unique_together = ("title", "version")
        verbose_name = "Item"
        verbose_name_plural = "Items"

    # -----------------------------------------------------------------
    def get_next_version(self):
        """Logic to calculate the next version string based on this item's version."""
        match = re.search(r"(\d+)(?!.*\d)", self.version)
        if match:
            number = int(match.group(1))
            return (
                self.version[: match.start()] + str(number + 1) + self.version[match.end():]
            )
        return f"{self.version}.1"
