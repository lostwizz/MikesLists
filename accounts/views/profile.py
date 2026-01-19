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
__updated__ = "2026-01-18 20:54:29"
###############################################################################

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.forms.custom_form import CustomUserChangeForm

# views.py
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})
