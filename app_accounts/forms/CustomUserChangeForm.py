#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
CustomUserChangeForm.py
app_accounts.forms.CustomUserChangeForm
/srv/django/MikesLists_dev/app_accounts/forms/CustomUserChangeForm.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 00:51:13"
###############################################################################

from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserChangeForm

class CustomUserChangeForm(UserChangeForm):
    password = None

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if 'groups' in self.fields:
            if self.request and not self.request.user.is_superuser:
                # Filter the queryset to ONLY what the user actually belongs to
                self.fields['groups'].queryset = self.instance.groups.all()
                self.fields['groups'].disabled = True


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'groups')
