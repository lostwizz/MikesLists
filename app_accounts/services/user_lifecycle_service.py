#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
user_lifecycle_service.py
app_accounts.services.user_lifecycle_service
/srv/django/MikesLists_dev/app_accounts/services/user_lifecycle_service.py



"""
__version__ = "0.0.0.000029-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-14 22:38:10"
###############################################################################


from django.db import transaction
from django.contrib.auth.models import User, Group
from app_accounts.models.profile import Profile
from app_accounts.utils.roles import assign_role_to_user



class UserLifecycleService:
    @staticmethod
    @transaction.atomic
    def register_user(username, email, password, role="Viewer"):
        """Creates a user and ensures they have a profile and starting role."""
        user = User.objects.create_user(username=username, email=email, password=password)
        # Profile is usually created via signals, so we just assign the role
        assign_role_to_user(user, role)
        return user

    @staticmethod
    @transaction.atomic
    def delete_user_safely(user_id):
        """Removes user and performs any necessary cleanup (logging, etc)."""
        user = User.objects.get(id=user_id)
        # Add logic here to reassign their ToDo lists to an 'Archive' user if needed
        user.delete()
        return True

    @staticmethod
    def promote_user(user, role_name):
        """Cleanly switches or adds a role to a user."""
        # You can decide to clear old roles or just add the new one
        return assign_role_to_user(user, role_name, clear_existing=True)
