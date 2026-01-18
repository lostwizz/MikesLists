#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
register.py
accounts.views.register
/srv/django/MikesLists_dev/accounts/views/register.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 15:19:27"
###############################################################################


from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.forms import CustomUserCreationForm

from ..forms.custom_form import CustomUserCreationForm

# Change the import to include UserCreationForm with Email
# or just use the standard one but add the field:

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            # This will show you exactly why the form failed in the terminal
            print(f"DEBUG: Form errors: {form.errors}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})
