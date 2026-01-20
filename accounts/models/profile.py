#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
profile.py
accounts.models.profile
/srv/django/MikesLists_dev/accounts/models/profile.py




"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 22:46:26"
###############################################################################


from django.db import models
from django.contrib.auth.models import User, Group

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme_preference = models.CharField(max_length=10, default='dark')
    email_notifications = models.BooleanField(default=True)
    # Groups are handled via the User model's many-to-many relationship

    class Meta:
        permissions = [
            ("view_my_profile", "Can view my profile"),
            ("edit_my_profile", "Can edit my profile"),
        ]
