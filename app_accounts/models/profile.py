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
from django.contrib.auth.models import User
import base64  # CRITICAL: Missing in your version
from PIL import Image
import io

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    email_notifications = models.BooleanField(default=True)
    timezone = models.CharField(max_length=50, default='UTC')

    # MariaDB BLOB Storage
    avatar_blob = models.BinaryField(null=True, blank=True)
    avatar_mimetype = models.CharField(max_length=20, default='image/jpeg')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_base64(self):
        """Converts binary data to a format HTML can understand"""
        if not self.avatar_blob:
            return None
        # Convert bytes to base64 string
        try:
            base64_data = base64.b64encode(self.avatar_blob).decode('utf-8')
            return f"data:{self.avatar_mimetype};base64,{base64_data}"
        except Exception:
            return None

    # Simplified save - no need to resize here if you do it in the view/form
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    class Meta:
        permissions = [
            ("view_my_profile", "Can view own profile"),
            ("edit_my_profile", "Can edit own profile"),
        ]
