#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
lists.py
app_ToDo.models.lists
/srv/django/MikesLists_dev/app_ToDo/models/lists.py


    ToDo app's lists.py



            ## - these a are allready defined automatically
        # permissions = [
        #     ("add_lists", "Can add lists"),
        #     ("change_lists", "Can change lists"),
        #     ("delete_lists", "Can delete lists"),
        #     ("view_lists", "Can view lists"),
        # ]

Since this is a structural change, you need to migrate:

        Generate Migration: python manage.py makemigrations ToDo --settings=MikesLists.settings.dev
        View the SQL (to see your linking table): python manage.py sqlmigrate ToDo [new_migration_number] --settings=MikesLists.settings.dev
        You will notice a new CREATE TABLE ToDo_lists_items ... in the pretty output!
        Apply Migration: python manage.py migrate ToDo --settings=MikesLists.settings.dev


should be able to do these:
    my_list.items.all()
    my_list.items.add(item)
    my_list.items.remove(item)
    item.lists.all()





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
__updated__ = "2026-01-23 01:17:00"
###############################################################################

from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

# Create your models here.
from .items import Items


# =================================================================
# =================================================================
class Lists(models.Model):
    #  id= bigint?????
    title = models.CharField(max_length=200)
    short_title = models.CharField(max_length=25, blank=True, null=True, default="")
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    visibility_allowed_groups = models.ManyToManyField(Group, blank=True)

    # This creates the hidden linking table automatically
    items = models.ManyToManyField(Items, related_name="lists", blank=True)

    # -----------------------------------------------------------------
    def __str__(self):
        return self.title

    # =================================================================
    class Meta:
        verbose_name = "List"
        verbose_name_plural = "Lists"
        ordering = ["title"]

    # -----------------------------------------------------------------
    def is_visible_to(self, user):
        return self.visibility_allowed_groups.filter(id__in=user.groups.all()).exists()

    # -----------------------------------------------------------------
    def add_item(self, item):
        self.items.add(item)

    # -----------------------------------------------------------------
    def remove_item(self, item):
        self.items.remove(item)
