#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
item_forms.py
item_forms
/srv/django/MikesLists_dev/ToDo/forms/item_forms.py




"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 20:42:48"
###############################################################################

from django import forms

from ToDo.models.items import Items


class ItemForm(forms.ModelForm):
    class Meta:
        model = Items
        fields = ["title", "typeflag", "status"]  # Add other fields as needed
