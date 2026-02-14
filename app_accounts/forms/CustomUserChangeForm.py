#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
CustomUserChangeForm.py
app_accounts.forms.CustomUserChangeForm
/srv/django/MikesLists_dev/app_accounts/forms/CustomUserChangeForm.py




"""
__version__ = "0.0.0.000013-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-12 23:11:45"
###############################################################################

from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserChangeForm


class CustomUserChangeForm(UserChangeForm):
    password = None

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        # Extract request if provided
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # If the form doesn't have a groups field, nothing to do
        groups_field = self.fields.get("groups")
        # if groups_field is None:
        #     return

        # If no request or user is superuser → leave queryset unchanged
        user = getattr(self.request, "user", None)
        if user is None or user.is_superuser:
            return

        # Non-superuser → restrict groups to only those the instance belongs to
        groups_field.queryset = self.instance.groups.all()
        groups_field.disabled = True

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username", "groups")
