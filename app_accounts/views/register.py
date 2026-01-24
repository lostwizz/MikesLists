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
__updated__ = "2026-01-23 21:08:25"
###############################################################################


from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.contrib import messages
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.forms import CustomUserCreationForm

# from ..forms.custom_form import CustomUserCreationForm

# Change the import to include UserCreationForm with Email
# or just use the standard one but add the field:

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # UPDATED LINE BELOW:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, f"Registration successful! Welcome, {user.username}.")

            # NOTE: You might want to change this redirect to "accounts:dashboard"
            # to avoid the root redirect loop we discussed earlier!
            return redirect('accounts:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
