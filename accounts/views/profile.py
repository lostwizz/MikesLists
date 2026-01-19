#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
profile.py
accounts.views.profile
/srv/django/MikesLists_dev/accounts/views/profile.py

"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 23:11:39"
###############################################################################

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
# from accounts.forms.CustomUserChangeForm import CustomUserChangeForm
from ..forms.CustomUserChangeForm import CustomUserChangeForm
from django.contrib import messages  # For the "Success" alert

# views.py
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('accounts:profile_view')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})



@login_required
def profile_view(request):
    """Simple read-only view of the user's profile."""
    return render(request, 'accounts/profile_detail.html', {'user': request.user})
