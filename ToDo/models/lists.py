#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
lists.py
ToDo.models.lists
/srv/django/MikesLists_dev/ToDo/models/lists.py

    ToDo app's lists.py


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

"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 20:41:11"
###############################################################################

from django.db import models

# Create your models here.
from .items import Items


# =================================================================
# =================================================================
class Lists(models.Model):
    #  id= bigint?????
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # This creates the hidden linking table automatically
    items = models.ManyToManyField(Items, related_name="lists", blank=True)

    # -----------------------------------------------------------------
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "List"
        verbose_name_plural = "Lists"


def funcname(parameter_list):
    """
    docstring
    """
    pass
    # # Get a specific list
    # my_list = Lists.objects.get(id=1)

    # # See all items in this list
    # all_items = my_list.items.all()
