#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
profileForm.py
app_accounts.forms.profileForm
/srv/django/MikesLists_dev/app_accounts/forms/profileForm.py






"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 14:27:43"
###############################################################################

from django import forms
from django.contrib.auth.models import User
from ..models.profile import Profile

class UserUpdateForm(forms.ModelForm):
    """Form to update basic User data (Username/Email)"""
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    """Form to update Profile-specific data (Bio, Avatar, Preferences)"""
    # Standalone field for MariaDB BLOB handling in the view
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'theme_preference', 'email_notifications']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'location': forms.TextInput(),
            'theme_preference': forms.Select(),
            'email_notifications': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes dynamically
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
