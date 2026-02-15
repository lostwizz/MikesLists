#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
user_registration_service.py
app_accounts.services.user_registration_service
/srv/django/MikesLists_dev/app_accounts/services/user_registration_service.py



"""
__version__ = "0.0.0.000029-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-14 22:36:55"
###############################################################################


from django.db import transaction
from django.contrib.auth.models import User, Group
from app_accounts.models.profile import Profile
from app_accounts.utils.roles import assign_role_to_user

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
