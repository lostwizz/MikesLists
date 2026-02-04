#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
group_manager.py
app_accounts.models.group_manager
/srv/django/MikesLists_dev/app_accounts/models/group_manager.py



"""
__version__ = "0.0.0.000025-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-02 14:00:58"
###############################################################################

# app_accounts/models/group_manager.py
from django.db import models

class GroupManager(models.Manager):
    """
    Custom manager for handling Role/Group operations within app_accounts.
    """
    def create_role(self, name, permissions=None):
        """Helper to create a group and assign permissions in one go."""
        group, created = self.get_or_create(name=name)
        if permissions:
            group.permissions.set(permissions)
        return group

    def get_by_name(self, name):
        """Helper to fetch a group safely by its name."""
        return self.filter(name=name).first()
