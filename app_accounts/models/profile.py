#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
profile.py
app_accounts.models.profile
/srv/django/MikesLists_dev/app_accounts/models/profile.py





"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:01:16"
###############################################################################


from django.db import models
from django.contrib.auth.models import User, Group

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     theme_preference = models.CharField(max_length=10, default='dark')
#     email_notifications = models.BooleanField(default=True)
#     # Groups are handled via the User model's many-to-many relationship

#     class Meta:
#         permissions = [
#             ("view_my_profile", "Can view my profile"),
#             ("edit_my_profile", "Can edit my profile"),
#         ]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # New field for the Middleware
    last_seen = models.DateTimeField(null=True, blank=True)

    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    email_notifications = models.BooleanField(default=True)

    # Pro Technical additions
    timezone = models.CharField(max_length=50, default='UTC')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def email(self):
        """Shortcut to get email from the User model."""
        return self.user.email


    def __str__(self):
        return f"{self.user.username}'s Profile"
