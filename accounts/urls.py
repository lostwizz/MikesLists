#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py




"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-17 22:09:52"
###############################################################################


# from django.urls import path
# from django.contrib.auth import views as auth_views
# from .views import login as custom_views  # if you wrote your own

# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views  # The dot means "from this current folder"


app_name = 'accounts'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='accounts/login.html'),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]
