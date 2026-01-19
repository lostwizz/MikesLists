#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
CustomUserChangeForm.py
accounts.forms.CustomUserChangeForm
/srv/django/MikesLists_dev/accounts/forms/CustomUserChangeForm.py

"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 20:57:54"
###############################################################################

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

class CustomUserChangeForm(UserChangeForm):
    # If you want to password to be read-only or hidden
    password = None

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
