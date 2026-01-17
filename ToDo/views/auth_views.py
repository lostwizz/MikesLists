#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
auth_views.py

    ToDo app's views.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-16 22:23:35"
###############################################################################


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

# from ...models.lists import Lists
# from ...models.items import Items


# -----------------------------------------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('list_management')
        else:
            # Handle login failure
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'login.html')




# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
