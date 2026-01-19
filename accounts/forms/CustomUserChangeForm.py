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
__updated__ = "2026-01-18 20:56:05"
###############################################################################

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserChangeForm(UserChangeForm):
    pass
