#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
services.py
app_accounts.services.services
/srv/django/MikesLists_dev/app_accounts/services/services.py


"""
__version__ = "0.0.0.000028-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 13:28:46"
###############################################################################


from django.db import transaction
from django.contrib.auth.models import User, Group
from .models import Profile
from .utils.roles import assign_role_to_user

class UserRegistrationService:
    @staticmethod
    @transaction.atomic
    def register_new_user(user_data):
        """
        Handles the entire sequence of creating a new user.
        transaction.atomic ensures if one part fails, the whole thing rolls back.
        """
        # 1. Create the base User
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )

        # 2. Profile is usually created by signals, but we can
        # update extra fields here if needed.
        profile = user.profile
        profile.bio = user_data.get('bio', '')
        profile.save()

        # 3. Assign Default Role
        assign_role_to_user(user, "Viewer")

        return user


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
