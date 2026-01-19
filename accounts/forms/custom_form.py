#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
custom_form.py
accounts.forms.custom_form
/srv/django/MikesLists_dev/accounts/forms/custom_form.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 15:45:24"
###############################################################################


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required for password recovery.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
