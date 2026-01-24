#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py
app_accounts.urls
/srv/django/MikesLists_dev/app_accounts/urls.py




"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 20:19:05"
###############################################################################

from django.contrib.auth import views as auth_views
from django.urls import path, include
from .views import register, profile_view, edit_profile
from .views.group_manager import group_manager
from .views.dashboard import dashboard

app_name = 'accounts'

from django.contrib.auth.views import LogoutView

class LogoutAllowGet(LogoutView):
    http_method_names = ["get", "post", "head", "options"]



urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    # path('logout/', LogoutAllowGet.as_view(), name='logout'),
    path("logout/", auth_views.LogoutView.as_view(next_page="accounts:login"), name="logout"),

    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),



    # Django auth URLs (login, logout, password reset, etc.)
    # path('', include('django.contrib.auth.urls')),

    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),

    # Profile
    path('profile/', profile_view, name='profile_view'),
    path('profile/edit/', edit_profile, name='edit_profile'),

    # Groups
    path("groups/", group_manager, name="group_manager"),

    # Registration
    path('register/', register, name='register'),
]
