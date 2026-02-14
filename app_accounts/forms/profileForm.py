#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
profileForm.py
app_accounts.forms.profileForm
/srv/django/MikesLists_dev/app_accounts/forms/profileForm.py







"""
__version__ = "0.0.0.000012-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-12 23:14:17"
###############################################################################

from django import forms
from django.contrib.auth.models import User
from ..models.profile import Profile


class UserUpdateForm(forms.ModelForm):
    """Form to update basic User data (Username/Email)"""
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap class to all fields (no branching)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    """Form to update Profile-specific data (Bio, Avatar, Preferences)"""

    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Profile
        fields = ["bio", "location", "theme_preference", "email_notifications"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "location": forms.TextInput(),
            "theme_preference": forms.Select(),
            "email_notifications": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Normalize widget classes without branching
        for field in self.fields.values():
            widget = field.widget

            # Checkbox
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
                continue

            # Select dropdown
            if isinstance(widget, forms.Select):
                widget.attrs["class"] = "form-select"
                continue

            # Everything else
            widget.attrs["class"] = "form-control"
