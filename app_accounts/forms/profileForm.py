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
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    """Form to update basic User data (Username/Email)"""
    email = forms.EmailField()

    class __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to make it look professional
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    """Form to update Profile-specific data (Bio, Avatar, Preferences)"""

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'location', 'theme_preference', 'email_notifications']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'theme_preference': forms.Select(attrs={'class': 'form-select'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the avatar field has the bootstrap file input class
        self.fields['avatar'].widget.attrs.update({'class': 'form-control'})
