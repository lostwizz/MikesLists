#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py
accounts.urls
/srv/django/MikesLists_dev/accounts/urls.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 22:07:17"
###############################################################################


# from django.urls import path
# from django.contrib.auth import views as auth_views
# from .views import login as custom_views  # if you wrote your own

# accounts/urls.py
from django.urls import path, include
from .views import register
from django.contrib.auth import views as auth_views

from . import views

# from . import views  # The dot means "from this current folder"
# from .views import register as register_view # Import the module from your views folder
app_name = 'accounts'

#

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('register/', register, name='register'),
    path('', include('django.contrib.auth.urls')),
]
